from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
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


class GoalOut(BaseModel):
    horizon: str
    description: str
    updated_at: Optional[datetime] = None
    include_in_resume: bool = False


class GoalResumeInclusionIn(BaseModel):
    include_in_resume: bool


@router.get("", operation_id="list_goals")
def list_goals(session: Session = Depends(get_session)) -> list[GoalOut]:
    existing = {g.horizon: g for g in session.exec(select(CareerGoal)).all()}
    result = []
    for h in HORIZONS:
        goal = existing.get(h)
        if goal is None:
            result.append(GoalOut(horizon=h, description="", updated_at=None, include_in_resume=False))
        else:
            result.append(
                GoalOut(
                    horizon=h,
                    description=goal.description,
                    updated_at=goal.updated_at,
                    include_in_resume=goal.include_in_resume,
                )
            )
    return result


@router.put("/{horizon}", operation_id="update_goal")
def update_goal(horizon: str, payload: GoalIn, session: Session = Depends(get_session)) -> CareerGoal:
    if horizon not in HORIZONS:
        raise HTTPException(status_code=400, detail="Invalid horizon")
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


@router.put("/{horizon}/resume-inclusion", operation_id="set_goal_resume_inclusion")
def set_goal_resume_inclusion(
    horizon: str, payload: GoalResumeInclusionIn, session: Session = Depends(get_session)
) -> CareerGoal:
    if horizon not in HORIZONS:
        raise HTTPException(status_code=400, detail="Invalid horizon")
    goal = session.get(CareerGoal, horizon)
    if goal is None:
        goal = CareerGoal(horizon=horizon)
    goal.include_in_resume = payload.include_in_resume
    session.add(goal)
    session.commit()
    session.refresh(goal)
    return goal


@router.get("/history", operation_id="list_goal_history")
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
