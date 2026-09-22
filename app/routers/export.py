from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session, select

from app import llm
from app.db import get_session
from app.models import ExportSnapshot, Settings, Skill

router = APIRouter(prefix="/api/export", tags=["export"])


class GapCheckIn(BaseModel):
    job_description: str


@router.get("")
def list_exports(session: Session = Depends(get_session)) -> list[ExportSnapshot]:
    return session.exec(select(ExportSnapshot).order_by(ExportSnapshot.generated_at.desc())).all()


@router.post("")
def generate_export(session: Session = Depends(get_session)) -> ExportSnapshot:
    skills = session.exec(select(Skill)).all()
    summaries = [f"{s.name}（{s.category}）" for s in skills]

    settings = session.get(Settings, 1)
    content = llm.generate_resume(summaries, settings)

    snapshot = ExportSnapshot(content=content)
    session.add(snapshot)
    session.commit()
    session.refresh(snapshot)
    return snapshot


@router.post("/gap-check")
def gap_check(payload: GapCheckIn, session: Session = Depends(get_session)):
    skills = session.exec(select(Skill)).all()
    current_skills = [{"name": s.name, "category": s.category} for s in skills]

    settings = session.get(Settings, 1)
    return llm.gap_check(payload.job_description, current_skills, settings)
