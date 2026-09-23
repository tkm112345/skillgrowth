from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session, select

from app.db import get_session
from app.models import CareerGoal, CareerVision, EvidenceEntry, ReflectionLog, Skill

router = APIRouter(prefix="/api/reflection", tags=["reflection"])

EPOCH = datetime.min.replace(tzinfo=timezone.utc)


class ReflectionIn(BaseModel):
    note: str = ""


@router.get("/summary")
def get_summary(session: Session = Depends(get_session)) -> dict:
    last_log = session.exec(select(ReflectionLog).order_by(ReflectionLog.created_at.desc())).first()
    baseline = last_log.created_at if last_log else EPOCH

    new_skills = session.exec(select(Skill).where(Skill.first_observed_at > baseline)).all()
    new_activity = session.exec(select(EvidenceEntry).where(EvidenceEntry.created_at > baseline)).all()
    vision = session.get(CareerVision, 1)
    goals = session.exec(select(CareerGoal)).all()

    return {
        "last_reflected_at": last_log.created_at if last_log else None,
        "new_skills_count": len(new_skills),
        "new_activity_count": len(new_activity),
        "vision_updated": bool(vision and vision.updated_at > baseline),
        "updated_goal_horizons": [g.horizon for g in goals if g.updated_at > baseline],
    }


@router.post("")
def mark_reflected(payload: ReflectionIn = ReflectionIn(), session: Session = Depends(get_session)) -> ReflectionLog:
    entry = ReflectionLog(note=payload.note)
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return entry


@router.get("/history")
def list_reflection_history(
    limit: int = 5,
    offset: int = 0,
    session: Session = Depends(get_session),
) -> list[ReflectionLog]:
    query = select(ReflectionLog).order_by(ReflectionLog.created_at.desc()).offset(offset).limit(limit)
    return session.exec(query).all()
