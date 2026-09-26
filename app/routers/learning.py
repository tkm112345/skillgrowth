from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, func, select

from app import services
from app.db import get_session
from app.models import ActivityType, LearningActivity, Settings, Skill

router = APIRouter(prefix="/api/learning", tags=["learning"])


class LearningActivityIn(BaseModel):
    activity_type: str
    title: str
    activity_date: Optional[date] = None
    notes: str = ""


class ActivityTypeIn(BaseModel):
    label: str


class LearningResult(BaseModel):
    activity: LearningActivity
    linked_skills: list[Skill]


@router.get("")
def list_learning(session: Session = Depends(get_session)) -> list[LearningActivity]:
    return session.exec(select(LearningActivity).order_by(LearningActivity.activity_date.desc())).all()


@router.post("")
def create_learning(payload: LearningActivityIn, session: Session = Depends(get_session)) -> LearningResult:
    settings = session.get(Settings, 1)
    text = services.text_block(種別=payload.activity_type, タイトル=payload.title, メモ=payload.notes)
    # "certification" gets its own EvidenceEntry.source_type so the Activity
    # feed tags it the same way as the separate certificate-image upload
    # path (POST /api/evidence/image) does — every other activity_type
    # (reading, talk given/attended, other, any custom type) keeps the
    # generic "learning_activity" tag, which is the correct catch-all for
    # those.
    source_type = "certification" if payload.activity_type == "certification" else "learning_activity"
    entry, linked = services.record_evidence_and_extract(session, source_type, text, settings)
    activity = LearningActivity(**payload.model_dump(), evidence_id=entry.id)
    session.add(activity)
    session.commit()
    session.refresh(activity)
    return LearningResult(activity=activity, linked_skills=linked)


@router.delete("/{activity_id}")
def delete_learning(activity_id: str, session: Session = Depends(get_session)):
    activity = session.get(LearningActivity, activity_id)
    if activity:
        session.delete(activity)
        session.commit()
    return {"ok": True}


@router.get("/types")
def list_activity_types(session: Session = Depends(get_session)) -> list[ActivityType]:
    return session.exec(select(ActivityType).order_by(ActivityType.created_at.asc())).all()


@router.post("/types")
def create_activity_type(payload: ActivityTypeIn, session: Session = Depends(get_session)) -> ActivityType:
    label = payload.label.strip()
    if not label:
        raise HTTPException(status_code=400, detail="Label cannot be empty")
    if session.exec(select(ActivityType).where(func.lower(ActivityType.label) == label.lower())).first():
        raise HTTPException(status_code=400, detail="A type with this name already exists")
    activity_type = ActivityType(label=label)
    session.add(activity_type)
    session.commit()
    session.refresh(activity_type)
    return activity_type


@router.put("/types/{type_id}")
def update_activity_type(
    type_id: str, payload: ActivityTypeIn, session: Session = Depends(get_session)
) -> ActivityType:
    activity_type = session.get(ActivityType, type_id)
    if activity_type is None:
        raise HTTPException(status_code=404, detail="Activity type not found")
    if activity_type.is_protected:
        raise HTTPException(status_code=400, detail="This type cannot be renamed")
    label = payload.label.strip()
    if not label:
        raise HTTPException(status_code=400, detail="Label cannot be empty")
    duplicate = session.exec(select(ActivityType).where(func.lower(ActivityType.label) == label.lower())).first()
    if duplicate and duplicate.id != type_id:
        raise HTTPException(status_code=400, detail="A type with this name already exists")
    activity_type.label = label
    activity_type.translation_key = None
    session.add(activity_type)
    session.commit()
    session.refresh(activity_type)
    return activity_type


@router.delete("/types/{type_id}")
def delete_activity_type(type_id: str, session: Session = Depends(get_session)):
    activity_type = session.get(ActivityType, type_id)
    if activity_type:
        if activity_type.is_protected:
            raise HTTPException(status_code=400, detail="This type cannot be deleted")
        session.delete(activity_type)
        session.commit()
    return {"ok": True}
