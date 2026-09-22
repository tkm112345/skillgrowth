from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.db import get_session
from app.models import (
    CareerGoal,
    Education,
    Employment,
    EvidenceEntry,
    ExportSnapshot,
    ExternalLink,
    LearningActivity,
    Project,
    Skill,
    SkillLink,
)

router = APIRouter(prefix="/api/backup", tags=["backup"])


@router.get("/export")
def export_backup(session: Session = Depends(get_session)) -> dict:
    def dump(model):
        return [row.model_dump(mode="json") for row in session.exec(select(model)).all()]

    return {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "evidence": dump(EvidenceEntry),
        "skills": dump(Skill),
        "skill_links": dump(SkillLink),
        "career_goals": dump(CareerGoal),
        "education": dump(Education),
        "employment": dump(Employment),
        "projects": dump(Project),
        "learning_activities": dump(LearningActivity),
        "external_links": dump(ExternalLink),
        "resume_exports": dump(ExportSnapshot),
    }
