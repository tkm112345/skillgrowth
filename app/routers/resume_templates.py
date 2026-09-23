import json
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlmodel import Session, select

from app.db import RESUME_TEMPLATE_DIR, get_session
from app.models import ResumeTemplate
from app.resume_docx import SECTION_FORMAT_CHOICES, render_resume_docx

router = APIRouter(prefix="/api/resume-templates", tags=["resume_templates"])


class ResumeTemplateUpdateIn(BaseModel):
    name: str | None = None
    section_formats: dict[str, str] | None = None
    is_selected: bool | None = None


def _validate_section_formats(section_formats: dict[str, str]) -> None:
    for key, value in section_formats.items():
        choices = SECTION_FORMAT_CHOICES.get(key)
        if choices is None or value not in choices:
            raise HTTPException(status_code=400, detail=f"Invalid section format: {key}={value}")


def _select_only(session: Session, entry: ResumeTemplate) -> None:
    for other in session.exec(select(ResumeTemplate).where(ResumeTemplate.is_selected == True)).all():  # noqa: E712
        other.is_selected = False
        session.add(other)
    entry.is_selected = True
    session.add(entry)


@router.get("")
def list_resume_templates(session: Session = Depends(get_session)) -> list[ResumeTemplate]:
    return session.exec(select(ResumeTemplate).order_by(ResumeTemplate.uploaded_at.desc())).all()


@router.post("")
def upload_resume_template(
    name: str = Form(...),
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
) -> ResumeTemplate:
    if not (file.filename or "").lower().endswith(".docx"):
        raise HTTPException(status_code=400, detail="Only .docx files are supported")

    is_first = session.exec(select(ResumeTemplate)).first() is None

    dest = RESUME_TEMPLATE_DIR / f"{uuid.uuid4()}.docx"
    dest.write_bytes(file.file.read())

    entry = ResumeTemplate(name=name, file_path=str(dest))
    session.add(entry)
    session.flush()
    if is_first:
        _select_only(session, entry)  # the first template becomes usable by default
    session.commit()
    session.refresh(entry)
    return entry


@router.put("/{template_id}")
def update_resume_template(
    template_id: str, payload: ResumeTemplateUpdateIn, session: Session = Depends(get_session)
) -> ResumeTemplate:
    entry = session.get(ResumeTemplate, template_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Resume template not found")
    if payload.name is not None:
        entry.name = payload.name
    if payload.section_formats is not None:
        _validate_section_formats(payload.section_formats)
        entry.section_formats = json.dumps(payload.section_formats)
    session.add(entry)
    if payload.is_selected:
        _select_only(session, entry)
    session.commit()
    session.refresh(entry)
    return entry


@router.delete("/{template_id}")
def delete_resume_template(template_id: str, session: Session = Depends(get_session)):
    entry = session.get(ResumeTemplate, template_id)
    if entry:
        Path(entry.file_path).unlink(missing_ok=True)
        session.delete(entry)
        session.commit()
    return {"ok": True}


@router.post("/{template_id}/generate")
def generate_resume_docx(template_id: str, session: Session = Depends(get_session)) -> StreamingResponse:
    entry = session.get(ResumeTemplate, template_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Resume template not found")
    content = render_resume_docx(session, entry)
    filename = f"resume-{entry.name}.docx".replace(" ", "_")
    return StreamingResponse(
        iter([content]),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
