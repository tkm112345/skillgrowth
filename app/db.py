from pathlib import Path

from sqlmodel import Session, SQLModel, create_engine, select

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)
UPLOAD_DIR = DATA_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
RESUME_TEMPLATE_DIR = UPLOAD_DIR / "resume_templates"
RESUME_TEMPLATE_DIR.mkdir(exist_ok=True)
PORTFOLIO_DIR = UPLOAD_DIR / "portfolio"
PORTFOLIO_DIR.mkdir(exist_ok=True)

engine = create_engine(f"sqlite:///{DATA_DIR / 'skillgrowth.db'}")


def _ensure_column(target_engine, table: str, column: str, ddl_type: str) -> None:
    # SQLModel.metadata.create_all() only creates missing tables — it never
    # alters an existing table's schema. This app has no Alembic (or other
    # migration tool), so a column added to a model after the table already
    # exists on disk needs to be backfilled by hand, or every existing
    # install crashes the first time that column is written to.
    with target_engine.connect() as conn:
        existing = {row[1] for row in conn.exec_driver_sql(f"PRAGMA table_info({table})")}
        if column not in existing:
            conn.exec_driver_sql(f"ALTER TABLE {table} ADD COLUMN {column} {ddl_type}")
            conn.commit()


def default_activity_types() -> list:
    from app.models import ActivityType  # noqa: PLC0415 (avoid circular import at module load)

    return [
        ActivityType(label="Reading", translation_key="typeReading"),
        ActivityType(label="Talk given", translation_key="typeTalkGiven"),
        ActivityType(label="Talk attended", translation_key="typeTalkAttended"),
        ActivityType(label="certification", is_protected=True, translation_key="typeCertification"),
        ActivityType(label="Other", translation_key="typeOther"),
    ]


def init_db() -> None:
    from app.models import ActivityType, Settings  # noqa: PLC0415 (avoid circular import at module load)

    SQLModel.metadata.create_all(engine)
    _ensure_column(engine, "exportsnapshot", "edited_at", "TIMESTAMP")
    _ensure_column(engine, "selfpr", "is_selected", "BOOLEAN DEFAULT 0")
    _ensure_column(engine, "skill", "include_in_resume", "BOOLEAN DEFAULT 1")
    _ensure_column(engine, "settings", "skill_extraction_enabled", "BOOLEAN DEFAULT 0")
    _ensure_column(engine, "reflectionlog", "note", "TEXT DEFAULT ''")
    with Session(engine) as session:
        if session.get(Settings, 1) is None:
            session.add(Settings(id=1))
            session.commit()
        if session.exec(select(ActivityType)).first() is None:
            session.add_all(default_activity_types())
            session.commit()


def get_session():
    # expire_on_commit=False: handlers often return an ORM object after one or
    # more session.commit() calls (e.g. evidence -> skill extraction -> link).
    # With the default expire_on_commit=True, commit() clears the object's
    # __dict__; Pydantic's serializer reads __dict__ directly (it doesn't
    # trigger SQLAlchemy's lazy-reload descriptors), so the response would
    # silently serialize as {}.
    with Session(engine, expire_on_commit=False) as session:
        yield session
