import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlmodel import Session, select

from app.db import RIREKISHO_TEMPLATE_DIR, get_session
from app.models import RirekishoTemplate
from app.rirekisho_docx import render_rirekisho_docx

router = APIRouter(prefix="/api/rirekisho-templates", tags=["rirekisho_templates"])


class RirekishoTemplateUpdateIn(BaseModel):
    name: str | None = None
    is_selected: bool | None = None


def _select_only(session: Session, entry: RirekishoTemplate) -> None:
    for other in session.exec(select(RirekishoTemplate).where(RirekishoTemplate.is_selected == True)).all():  # noqa: E712
        other.is_selected = False
        session.add(other)
    entry.is_selected = True
    session.add(entry)


@router.get("")
def list_rirekisho_templates(session: Session = Depends(get_session)) -> list[RirekishoTemplate]:
    return session.exec(select(RirekishoTemplate).order_by(RirekishoTemplate.uploaded_at.desc())).all()


@router.post("")
def upload_rirekisho_template(
    name: str = Form(...),
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
) -> RirekishoTemplate:
    if not (file.filename or "").lower().endswith(".docx"):
        raise HTTPException(status_code=400, detail="Only .docx files are supported")

    is_first = session.exec(select(RirekishoTemplate)).first() is None

    dest = RIREKISHO_TEMPLATE_DIR / f"{uuid.uuid4()}.docx"
    dest.write_bytes(file.file.read())

    entry = RirekishoTemplate(name=name, file_path=str(dest))
    session.add(entry)
    session.flush()
    if is_first:
        _select_only(session, entry)  # the first template becomes usable by default
    session.commit()
    session.refresh(entry)
    return entry


@router.put("/{template_id}")
def update_rirekisho_template(
    template_id: str, payload: RirekishoTemplateUpdateIn, session: Session = Depends(get_session)
) -> RirekishoTemplate:
    entry = session.get(RirekishoTemplate, template_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Rirekisho template not found")
    if payload.name is not None:
        entry.name = payload.name
    session.add(entry)
    if payload.is_selected:
        _select_only(session, entry)
    session.commit()
    session.refresh(entry)
    return entry


@router.delete("/{template_id}")
def delete_rirekisho_template(template_id: str, session: Session = Depends(get_session)):
    entry = session.get(RirekishoTemplate, template_id)
    if entry:
        Path(entry.file_path).unlink(missing_ok=True)
        session.delete(entry)
        session.commit()
    return {"ok": True}


@router.post("/{template_id}/generate")
def generate_rirekisho_docx(template_id: str, session: Session = Depends(get_session)) -> StreamingResponse:
    entry = session.get(RirekishoTemplate, template_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Rirekisho template not found")
    content = render_rirekisho_docx(session, entry)
    filename = f"rirekisho-{entry.name}.docx".replace(" ", "_")
    return StreamingResponse(
        iter([content]),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
