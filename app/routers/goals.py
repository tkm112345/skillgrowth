from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session, select

from app.db import get_session
from app.models import CareerGoal, CareerGoalHistory

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
    if goal.description != payload.description:
        session.add(CareerGoalHistory(horizon=horizon, description=payload.description))
    goal.description = payload.description
    goal.updated_at = datetime.now(timezone.utc)
    session.add(goal)
    session.commit()
    session.refresh(goal)
    return goal


@router.get("/history")
def list_goal_history(
    horizon: Optional[str] = None,
    limit: int = 5,
    offset: int = 0,
    session: Session = Depends(get_session),
) -> list[CareerGoalHistory]:
    query = select(CareerGoalHistory)
    if horizon:
        query = query.where(CareerGoalHistory.horizon == horizon)
    query = query.order_by(CareerGoalHistory.created_at.desc()).offset(offset).limit(limit)
    return session.exec(query).all()
