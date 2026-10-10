import json
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlmodel import Session, select

from app.db import RESUME_MD_TEMPLATE_DIR, get_session
from app.models import ResumeMdTemplate
from app.resume_docx import SECTION_FORMAT_CHOICES
from app.resume_markdown_template import render_resume_markdown_template
from app.services import select_only, validate_section_formats

router = APIRouter(prefix="/api/resume-md-templates", tags=["resume_md_templates"])


class ResumeMdTemplateUpdateIn(BaseModel):
    name: str | None = None
    section_formats: dict[str, str] | None = None
    is_selected: bool | None = None


@router.get("")
def list_resume_md_templates(session: Session = Depends(get_session)) -> list[ResumeMdTemplate]:
    return session.exec(select(ResumeMdTemplate).order_by(ResumeMdTemplate.uploaded_at.desc())).all()


@router.post("")
def upload_resume_md_template(
    name: str = Form(...),
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
) -> ResumeMdTemplate:
    if not (file.filename or "").lower().endswith(".md"):
        raise HTTPException(status_code=400, detail="Only .md files are supported")

    is_first = session.exec(select(ResumeMdTemplate)).first() is None

    dest = RESUME_MD_TEMPLATE_DIR / f"{uuid.uuid4()}.md"
    dest.write_bytes(file.file.read())

    entry = ResumeMdTemplate(name=name, file_path=str(dest))
    session.add(entry)
    session.flush()
    if is_first:
        select_only(session, entry)  # the first template becomes usable by default
    session.commit()
    session.refresh(entry)
    return entry


@router.put("/{template_id}")
def update_resume_md_template(
    template_id: str, payload: ResumeMdTemplateUpdateIn, session: Session = Depends(get_session)
) -> ResumeMdTemplate:
    entry = session.get(ResumeMdTemplate, template_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Resume Markdown template not found")
    if payload.name is not None:
        entry.name = payload.name
    if payload.section_formats is not None:
        validate_section_formats(payload.section_formats, SECTION_FORMAT_CHOICES)
        entry.section_formats = json.dumps(payload.section_formats)
    session.add(entry)
    if payload.is_selected:
        select_only(session, entry)
    session.commit()
    session.refresh(entry)
    return entry


@router.delete("/{template_id}")
def delete_resume_md_template(template_id: str, session: Session = Depends(get_session)):
    entry = session.get(ResumeMdTemplate, template_id)
    if entry:
        Path(entry.file_path).unlink(missing_ok=True)
        session.delete(entry)
        session.commit()
    return {"ok": True}


@router.post("/{template_id}/generate")
def generate_resume_markdown_from_template(
    template_id: str, session: Session = Depends(get_session)
) -> StreamingResponse:
    entry = session.get(ResumeMdTemplate, template_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Resume Markdown template not found")
    content = render_resume_markdown_template(session, entry)
    filename = f"resume-{entry.name}.md".replace(" ", "_")
    return StreamingResponse(
        iter([content.encode("utf-8")]),
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
