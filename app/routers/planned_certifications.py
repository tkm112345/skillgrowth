from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from app import services
from app.db import get_session
from app.models import LearningActivity, PlannedCertification, Settings

router = APIRouter(prefix="/api/planned-certifications", tags=["planned-certifications"])

PLANNED_CERTIFICATION_STATUSES = {"considering", "planned"}


class PlannedCertificationIn(BaseModel):
    title: str
    status: str
    target_date: Optional[date] = None
    notes: str = ""


class PromoteIn(BaseModel):
    activity_date: Optional[date] = None


def _validate_status(status: str) -> None:
    if status not in PLANNED_CERTIFICATION_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid status")


@router.get("", operation_id="list_planned_certifications")
def list_planned_certifications(session: Session = Depends(get_session)) -> list[PlannedCertification]:
    return session.exec(select(PlannedCertification).order_by(PlannedCertification.created_at.asc())).all()


@router.post("", operation_id="add_planned_certification")
def create_planned_certification(
    payload: PlannedCertificationIn, session: Session = Depends(get_session)
) -> PlannedCertification:
    _validate_status(payload.status)
    title = payload.title.strip()
    if not title:
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    planned = PlannedCertification(
        title=title, status=payload.status, target_date=payload.target_date, notes=payload.notes
    )
    session.add(planned)
    session.commit()
    session.refresh(planned)
    return planned


@router.put("/{planned_id}", operation_id="update_planned_certification")
def update_planned_certification(
    planned_id: str, payload: PlannedCertificationIn, session: Session = Depends(get_session)
) -> PlannedCertification:
    planned = session.get(PlannedCertification, planned_id)
    if planned is None:
        raise HTTPException(status_code=404, detail="Planned certification not found")
    _validate_status(payload.status)
    title = payload.title.strip()
    if not title:
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    planned.title = title
    planned.status = payload.status
    planned.target_date = payload.target_date
    planned.notes = payload.notes
    session.add(planned)
    session.commit()
    session.refresh(planned)
    return planned


@router.delete("/{planned_id}")
def delete_planned_certification(planned_id: str, session: Session = Depends(get_session)):
    planned = session.get(PlannedCertification, planned_id)
    if planned:
        session.delete(planned)
        session.commit()
    return {"ok": True}


@router.post("/{planned_id}/promote", operation_id="promote_planned_certification")
def promote_planned_certification(
    planned_id: str, payload: PromoteIn, session: Session = Depends(get_session)
) -> LearningActivity:
    """Converts a candidate into a regular certification entry through the
    same evidence/skill-extraction path manual entry uses
    (app/routers/learning.py::create_learning), so the result is
    indistinguishable from a hand-added certification. One endpoint rather
    than the frontend doing create-then-delete, so a dropped connection
    can't leave both a new LearningActivity and the original candidate
    behind."""
    planned = session.get(PlannedCertification, planned_id)
    if planned is None:
        raise HTTPException(status_code=404, detail="Planned certification not found")

    settings = session.get(Settings, 1)
    text = services.text_block(タイトル=planned.title, メモ=planned.notes)
    entry, _linked = services.record_evidence_and_extract(session, "certification", text, settings)

    activity = LearningActivity(
        activity_type="certification",
        title=planned.title,
        activity_date=payload.activity_date or date.today(),
        notes=planned.notes,
        evidence_id=entry.id,
    )
    session.add(activity)
    session.delete(planned)
    session.commit()
    session.refresh(activity)
    return activity
