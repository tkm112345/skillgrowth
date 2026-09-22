from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session, select

from app import services
from app.db import get_session
from app.models import LearningActivity, Settings

router = APIRouter(prefix="/api/learning", tags=["learning"])


class LearningActivityIn(BaseModel):
    activity_type: str
    title: str
    activity_date: Optional[date] = None
    notes: str = ""


@router.get("")
def list_learning(session: Session = Depends(get_session)) -> list[LearningActivity]:
    return session.exec(select(LearningActivity).order_by(LearningActivity.activity_date.desc())).all()


@router.post("")
def create_learning(payload: LearningActivityIn, session: Session = Depends(get_session)):
    settings = session.get(Settings, 1)
    text = services.text_block(種別=payload.activity_type, タイトル=payload.title, メモ=payload.notes)
    entry, linked = services.record_evidence_and_extract(session, "learning_activity", text, settings)
    activity = LearningActivity(**payload.model_dump(), evidence_id=entry.id)
    session.add(activity)
    session.commit()
    session.refresh(activity)
    return {"activity": activity, "linked_skills": linked}


@router.delete("/{activity_id}")
def delete_learning(activity_id: str, session: Session = Depends(get_session)):
    activity = session.get(LearningActivity, activity_id)
    if activity:
        session.delete(activity)
        session.commit()
    return {"ok": True}
