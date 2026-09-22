import json
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.backup_import import import_backup
from app.db import get_session
from app.models import (
    CareerGoal,
    CareerGoalHistory,
    CareerVision,
    ConsultMessage,
    ConsultSession,
    Education,
    Employment,
    EvidenceEntry,
    ExportSnapshot,
    ExternalLink,
    LearningActivity,
    Project,
    SampleDataRecord,
    SelfPR,
    Skill,
    SkillLink,
)

router = APIRouter(prefix="/api/backup", tags=["backup"])

SAMPLE_DATA_PATH = Path(__file__).resolve().parent.parent / "sample_data.json"

# Deletion order matters: children before the rows they reference.
RESET_TABLE_ORDER: list[tuple[str, type]] = [
    ("skill_link", SkillLink),
    ("project", Project),
    ("employment", Employment),
    ("education", Education),
    ("learning_activity", LearningActivity),
    ("external_link", ExternalLink),
    ("resume_export", ExportSnapshot),
    ("skill", Skill),
    ("evidence", EvidenceEntry),
    ("self_pr", SelfPR),
    ("career_goal_history", CareerGoalHistory),
    ("consult_message", ConsultMessage),
    ("consult_session", ConsultSession),
]


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
        "career_goal_history": dump(CareerGoalHistory),
        "career_vision": dump(CareerVision),
        "education": dump(Education),
        "employment": dump(Employment),
        "projects": dump(Project),
        "learning_activities": dump(LearningActivity),
        "external_links": dump(ExternalLink),
        "resume_exports": dump(ExportSnapshot),
        "self_prs": dump(SelfPR),
        "consult_sessions": dump(ConsultSession),
        "consult_messages": dump(ConsultMessage),
    }


@router.post("/import")
def import_backup_endpoint(payload: dict, session: Session = Depends(get_session)) -> dict:
    return import_backup(session, payload)


@router.post("/load-sample")
def load_sample_data(session: Session = Depends(get_session)) -> dict:
    data = json.loads(SAMPLE_DATA_PATH.read_text())
    track: dict[str, list[str]] = {}
    counts = import_backup(session, data, track=track)

    for table_name, ids in track.items():
        for record_id in ids:
            session.add(SampleDataRecord(table_name=table_name, record_id=record_id))
    session.commit()

    return counts


@router.post("/reset-sample")
def reset_sample_data(session: Session = Depends(get_session)) -> dict:
    records = session.exec(select(SampleDataRecord)).all()
    ids_by_table: dict[str, set[str]] = {}
    for r in records:
        ids_by_table.setdefault(r.table_name, set()).add(r.record_id)

    counts: dict[str, int] = {}
    for table_name, model in RESET_TABLE_ORDER:
        ids = ids_by_table.get(table_name, set())
        deleted = 0
        for record_id in ids:
            obj = session.get(model, record_id)
            if obj:
                session.delete(obj)
                deleted += 1
        counts[table_name] = deleted

    counts["career_goal"] = 0
    for horizon in ids_by_table.get("career_goal", set()):
        goal = session.get(CareerGoal, horizon)
        if goal:
            goal.description = ""
            session.add(goal)
            counts["career_goal"] += 1

    counts["career_vision"] = 0
    for _ in ids_by_table.get("career_vision", set()):
        vision = session.get(CareerVision, 1)
        if vision:
            vision.content = ""
            session.add(vision)
            counts["career_vision"] += 1

    for r in records:
        session.delete(r)

    session.commit()
    return counts
