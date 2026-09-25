from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session, select

from app import llm
from app.db import get_session
from app.models import CareerGoal, Settings, Skill
from app.routers.goals import HORIZON_LABELS, HORIZONS
from app.services import MAX_SKILLS_IN_PROMPT

router = APIRouter(prefix="/api/ai", tags=["ai"])


class GapCheckIn(BaseModel):
    job_description: str


def _current_skills_payload(session: Session) -> list[dict]:
    skills = session.exec(select(Skill).order_by(Skill.last_observed_at.desc()).limit(MAX_SKILLS_IN_PROMPT)).all()
    return [{"name": s.name, "category": s.category} for s in skills]


@router.post("/gap-check")
def gap_check(payload: GapCheckIn, session: Session = Depends(get_session)):
    settings = session.get(Settings, 1)
    return llm.gap_check(payload.job_description, _current_skills_payload(session), settings)


@router.post("/growth-guidance")
def growth_guidance(session: Session = Depends(get_session)) -> dict:
    existing = {g.horizon: g for g in session.exec(select(CareerGoal)).all()}
    goals_payload = [
        {"horizon": h, "horizon_label": HORIZON_LABELS[h], "description": existing[h].description}
        for h in HORIZONS
        if h in existing and existing[h].description.strip()
    ]
    if not goals_payload:
        return {"by_horizon": []}

    settings = session.get(Settings, 1)
    return llm.goal_growth_guidance(goals_payload, _current_skills_payload(session), settings)
