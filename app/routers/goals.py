from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session, select

from app import llm
from app.db import get_session
from app.models import CareerGoal, Settings, Skill

router = APIRouter(prefix="/api/goals", tags=["goals"])

HORIZONS = ["this_year", "5_years", "10_years"]
HORIZON_LABELS = {"this_year": "今年", "5_years": "5年後", "10_years": "10年後"}


class GoalIn(BaseModel):
    horizon: str
    description: str


@router.get("")
def list_goals(session: Session = Depends(get_session)) -> list[CareerGoal]:
    existing = {g.horizon: g for g in session.exec(select(CareerGoal)).all()}
    return [existing.get(h) or CareerGoal(horizon=h) for h in HORIZONS]


@router.put("/{horizon}")
def update_goal(horizon: str, payload: GoalIn, session: Session = Depends(get_session)) -> CareerGoal:
    goal = session.get(CareerGoal, horizon)
    if goal is None:
        goal = CareerGoal(horizon=horizon)
    goal.description = payload.description
    goal.updated_at = datetime.now(timezone.utc)
    session.add(goal)
    session.commit()
    session.refresh(goal)
    return goal


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
    skills = session.exec(select(Skill)).all()
    current_skills = [{"name": s.name, "category": s.category} for s in skills]
    return llm.goal_growth_guidance(goals_payload, current_skills, settings)
