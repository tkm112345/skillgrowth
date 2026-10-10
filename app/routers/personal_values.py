from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session

from app.db import get_session
from app.models import PersonalValues

router = APIRouter(prefix="/api/personal-values", tags=["personal_values"])


class PersonalValuesIn(BaseModel):
    content: str


class PersonalValuesOut(BaseModel):
    content: str
    updated_at: Optional[datetime] = None
    include_in_resume: bool = True


class PersonalValuesResumeInclusionIn(BaseModel):
    include_in_resume: bool


@router.get("", operation_id="get_personal_values")
def get_personal_values(session: Session = Depends(get_session)) -> PersonalValuesOut:
    values = session.get(PersonalValues, 1)
    if values is None:
        return PersonalValuesOut(content="", updated_at=None, include_in_resume=True)
    return PersonalValuesOut(
        content=values.content, updated_at=values.updated_at, include_in_resume=values.include_in_resume
    )


@router.put("", operation_id="update_personal_values")
def update_personal_values(payload: PersonalValuesIn, session: Session = Depends(get_session)) -> PersonalValues:
    values = session.get(PersonalValues, 1)
    if values is None:
        values = PersonalValues(id=1)
    values.content = payload.content
    values.updated_at = datetime.now(timezone.utc)
    session.add(values)
    session.commit()
    session.refresh(values)
    return values


@router.put("/resume-inclusion", operation_id="set_personal_values_resume_inclusion")
def set_personal_values_resume_inclusion(
    payload: PersonalValuesResumeInclusionIn, session: Session = Depends(get_session)
) -> PersonalValues:
    values = session.get(PersonalValues, 1)
    if values is None:
        values = PersonalValues(id=1)
    values.include_in_resume = payload.include_in_resume
    session.add(values)
    session.commit()
    session.refresh(values)
    return values
