import base64
import json
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends
from sqlmodel import Session, SQLModel, select

from app.backup_import import import_backup
from app.db import PORTFOLIO_DIR, RESUME_TEMPLATE_DIR, default_activity_types, get_session
from app.models import (
    ActivityType,
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
    PortfolioFile,
    PortfolioItem,
    PortfolioLink,
    Project,
    ReflectionLog,
    ResumeTemplate,
    SampleDataRecord,
    SelfFeedback,
    SelfPR,
    Settings,
    Skill,
    SkillLink,
)

router = APIRouter(prefix="/api/backup", tags=["backup"])

SAMPLE_DATA_PATH = Path(__file__).resolve().parent.parent / "sample_data.json"


def sample_record_ids(session: Session, table_name: str) -> set[str]:
    """The ids of every row `load-sample` tagged for the given table, so a
    list endpoint can mark which of its rows are sample-sourced (same
    `table_name` values `reset-sample` below already keys off of)."""
    return {
        r.record_id
        for r in session.exec(select(SampleDataRecord).where(SampleDataRecord.table_name == table_name)).all()
    }


# Deletion order matters: children before the rows they reference.
RESET_TABLE_ORDER: list[tuple[str, type]] = [
    ("skill_link", SkillLink),
    ("project", Project),
    ("employment", Employment),
    ("education", Education),
    ("learning_activity", LearningActivity),
    ("external_link", ExternalLink),
    ("resume_export", ExportSnapshot),
    ("resume_template", ResumeTemplate),
    ("portfolio_link", PortfolioLink),
    ("portfolio_file", PortfolioFile),
    ("portfolio_item", PortfolioItem),
    ("skill", Skill),
    ("evidence", EvidenceEntry),
    ("self_pr", SelfPR),
    ("career_goal_history", CareerGoalHistory),
    ("consult_message", ConsultMessage),
    ("consult_session", ConsultSession),
]


def _dump_resume_templates(session: Session) -> list[dict]:
    # Unlike EvidenceEntry's certificate images (path only, file not
    # included — see docs/ARCHITECTURE.md), a resume template is few and
    # deliberately authored, so its file content is embedded as base64
    # rather than just referencing a local path that a restore elsewhere
    # can't resolve.
    rows = []
    for row in session.exec(select(ResumeTemplate)).all():
        data = row.model_dump(mode="json")
        try:
            data["file_content_base64"] = base64.b64encode(Path(row.file_path).read_bytes()).decode("ascii")
        except FileNotFoundError:
            data["file_content_base64"] = None
        rows.append(data)
    return rows


def _dump_portfolio_files(session: Session) -> list[dict]:
    # Same reasoning as _dump_resume_templates: a portfolio file is few and
    # deliberately uploaded, so losing it on a restore elsewhere would be a
    # real loss, unlike EvidenceEntry's certificate images (path only).
    rows = []
    for row in session.exec(select(PortfolioFile)).all():
        data = row.model_dump(mode="json")
        try:
            data["file_content_base64"] = base64.b64encode(Path(row.file_path).read_bytes()).decode("ascii")
        except FileNotFoundError:
            data["file_content_base64"] = None
        rows.append(data)
    return rows


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
        "reflection_log": dump(ReflectionLog),
        "education": dump(Education),
        "employment": dump(Employment),
        "projects": dump(Project),
        "learning_activities": dump(LearningActivity),
        "activity_types": dump(ActivityType),
        "external_links": dump(ExternalLink),
        "resume_exports": dump(ExportSnapshot),
        "resume_templates": _dump_resume_templates(session),
        "portfolio_items": dump(PortfolioItem),
        "portfolio_links": dump(PortfolioLink),
        "portfolio_files": _dump_portfolio_files(session),
        "self_prs": dump(SelfPR),
        "self_feedback": dump(SelfFeedback),
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


@router.post("/reset-all")
def reset_all_data(session: Session = Depends(get_session)) -> dict:
    """Wipe every table and re-seed the same defaults a fresh install gets
    (the Settings singleton, the 5 default ActivityTypes) — everything,
    not just sample-tracked rows, including the LLM connection settings.

    Operates on `session.get_bind()`, not the module-level `app.db.engine`
    directly: tests override `get_session` to point at an isolated engine
    (see tests/conftest.py), and code that reaches for the module-level
    `engine` instead bypasses that override — this exact bug shipped once
    and a test run wiped the real `data/skillgrowth.db` a fresh install's
    `init_db()` (which does hardcode `app.db.engine`) can't be reused here
    for the same reason, so the reseed below is done directly against
    `bind` instead of calling it.

    Deliberately drop_all/create_all rather than a per-table DELETE list
    (like RESET_TABLE_ORDER above): a table added to a future model would
    silently be missed by a hand-maintained list, but never by this."""
    bind = session.get_bind()
    session.close()
    SQLModel.metadata.drop_all(bind)
    SQLModel.metadata.create_all(bind)

    with Session(bind) as fresh:
        fresh.add(Settings(id=1))
        fresh.add_all(default_activity_types())
        fresh.commit()

    for directory in (PORTFOLIO_DIR, RESUME_TEMPLATE_DIR):
        for f in directory.iterdir():
            if f.is_file():
                f.unlink()

    return {"ok": True}
