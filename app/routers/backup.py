import json
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.backup_import import import_backup
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

SAMPLE_DATA_PATH = Path(__file__).resolve().parent.parent / "sample_data.json"


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


@router.post("/import")
def import_backup_endpoint(payload: dict, session: Session = Depends(get_session)) -> dict:
    return import_backup(session, payload)


@router.post("/load-sample")
def load_sample_data(session: Session = Depends(get_session)) -> dict:
    data = json.loads(SAMPLE_DATA_PATH.read_text())
    return import_backup(session, data)
