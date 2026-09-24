from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from app.db import get_session
from app.models import ExportSnapshot
from app.resume_builder import build_resume_markdown

router = APIRouter(prefix="/api/export", tags=["export"])


class ExportContentIn(BaseModel):
    content: str


@router.get("")
def list_exports(limit: int = 20, offset: int = 0, session: Session = Depends(get_session)) -> list[ExportSnapshot]:
    return session.exec(
        select(ExportSnapshot).order_by(ExportSnapshot.generated_at.desc()).offset(offset).limit(limit)
    ).all()


@router.post("")
def generate_export(session: Session = Depends(get_session)) -> ExportSnapshot:
    content = build_resume_markdown(session)

    snapshot = ExportSnapshot(content=content)
    session.add(snapshot)
    session.commit()
    session.refresh(snapshot)
    return snapshot


@router.put("/{export_id}")
def update_export(export_id: str, payload: ExportContentIn, session: Session = Depends(get_session)) -> ExportSnapshot:
    snapshot = session.get(ExportSnapshot, export_id)
    if snapshot is None:
        raise HTTPException(status_code=404, detail="Resume snapshot not found")
    snapshot.content = payload.content
    snapshot.edited_at = datetime.now(timezone.utc)
    session.add(snapshot)
    session.commit()
    session.refresh(snapshot)
    return snapshot
