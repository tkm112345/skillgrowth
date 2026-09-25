from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from app.db import get_session
from app.models import SelfFeedback

router = APIRouter(prefix="/api/self-feedback", tags=["self_feedback"])


class SelfFeedbackIn(BaseModel):
    entry_date: date
    accomplishments: str = ""
    reflection: str = ""
    next_steps: str = ""


@router.get("")
def list_self_feedback(limit: int = 50, offset: int = 0, session: Session = Depends(get_session)) -> list[SelfFeedback]:
    return session.exec(select(SelfFeedback).order_by(SelfFeedback.entry_date.desc()).offset(offset).limit(limit)).all()


@router.post("")
def add_self_feedback(payload: SelfFeedbackIn, session: Session = Depends(get_session)) -> SelfFeedback:
    entry = SelfFeedback(**payload.model_dump())
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return entry


@router.put("/{entry_id}")
def update_self_feedback(
    entry_id: str, payload: SelfFeedbackIn, session: Session = Depends(get_session)
) -> SelfFeedback:
    entry = session.get(SelfFeedback, entry_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Self-feedback entry not found")

    entry.entry_date = payload.entry_date
    entry.accomplishments = payload.accomplishments
    entry.reflection = payload.reflection
    entry.next_steps = payload.next_steps
    entry.updated_at = datetime.now(timezone.utc)
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return entry


@router.delete("/{entry_id}")
def delete_self_feedback(entry_id: str, session: Session = Depends(get_session)):
    entry = session.get(SelfFeedback, entry_id)
    if entry:
        session.delete(entry)
        session.commit()
    return {"ok": True}
