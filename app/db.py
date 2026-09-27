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
PERSONAL_INFO_DIR = UPLOAD_DIR / "personal_info"
PERSONAL_INFO_DIR.mkdir(exist_ok=True)
RIREKISHO_TEMPLATE_DIR = UPLOAD_DIR / "rirekisho_templates"
RIREKISHO_TEMPLATE_DIR.mkdir(exist_ok=True)

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


def _ensure_index(target_engine, table: str, column: str) -> None:
    # Same problem as _ensure_column, different DDL: create_all() only adds
    # indexes to tables it's creating fresh — a `Field(index=True)` added to
    # a model whose table already exists on disk needs this, or an upgraded
    # install just silently never gets the index. Unlike ALTER TABLE ADD
    # COLUMN, SQLite's CREATE INDEX supports IF NOT EXISTS directly, so this
    # doesn't need _ensure_column's existence check first.
    with target_engine.connect() as conn:
        conn.exec_driver_sql(f"CREATE INDEX IF NOT EXISTS ix_{table}_{column} ON {table} ({column})")
        conn.commit()


# (table, entity_type, title_column, body_column) for every table the global
# search box (frontend GlobalSearch.vue, GET /api/search) covers.
_SEARCH_SOURCES = [
    ("skill", "skill", "name", "category"),
    ("learningactivity", "learning_activity", "title", "notes"),
    ("portfolioitem", "portfolio_item", "title", "description"),
]


def _ensure_search_index(target_engine) -> None:
    # search_index is a SQLite FTS5 virtual table, not a SQLModel-mapped
    # table, so create_all() never creates or touches it — and it holds a
    # copy of Skill/LearningActivity/PortfolioItem text rather than joining
    # to them live, so every write path (including app.backup_import's bulk
    # restore) needs to be mirrored here via triggers rather than in each
    # router. AFTER INSERT/UPDATE/DELETE triggers keep it in sync going
    # forward; the DELETE+re-INSERT below is a one-time backfill for
    # whatever already exists on disk (a no-op full rebuild on a fresh
    # install, cheap at this app's single-user scale).
    with target_engine.connect() as conn:
        conn.exec_driver_sql(
            "CREATE VIRTUAL TABLE IF NOT EXISTS search_index USING fts5("
            "entity_type UNINDEXED, entity_id UNINDEXED, title, body)"
        )
        for table, entity_type, title_col, body_col in _SEARCH_SOURCES:
            conn.exec_driver_sql(
                f"CREATE TRIGGER IF NOT EXISTS search_{table}_ai AFTER INSERT ON {table} BEGIN "
                f"INSERT INTO search_index(entity_type, entity_id, title, body) "
                f"VALUES ('{entity_type}', new.id, new.{title_col}, new.{body_col}); END"
            )
            conn.exec_driver_sql(
                f"CREATE TRIGGER IF NOT EXISTS search_{table}_au AFTER UPDATE ON {table} BEGIN "
                f"DELETE FROM search_index WHERE entity_type='{entity_type}' AND entity_id=old.id; "
                f"INSERT INTO search_index(entity_type, entity_id, title, body) "
                f"VALUES ('{entity_type}', new.id, new.{title_col}, new.{body_col}); END"
            )
            conn.exec_driver_sql(
                f"CREATE TRIGGER IF NOT EXISTS search_{table}_ad AFTER DELETE ON {table} BEGIN "
                f"DELETE FROM search_index WHERE entity_type='{entity_type}' AND entity_id=old.id; END"
            )
        conn.exec_driver_sql("DELETE FROM search_index")
        for table, entity_type, title_col, body_col in _SEARCH_SOURCES:
            conn.exec_driver_sql(
                f"INSERT INTO search_index(entity_type, entity_id, title, body) "
                f"SELECT '{entity_type}', id, {title_col}, {body_col} FROM {table}"
            )
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
    _ensure_column(engine, "settings", "consult_custom_instructions", "TEXT DEFAULT ''")
    _ensure_column(engine, "reflectionlog", "note", "TEXT DEFAULT ''")
    _ensure_column(engine, "skill", "proficiency", "INTEGER")
    _ensure_column(engine, "learningactivity", "include_in_resume", "BOOLEAN DEFAULT 1")
    _ensure_column(engine, "learningactivity", "expiry_date", "DATE")
    _ensure_column(engine, "consultsession", "target_industry", "TEXT")
    _ensure_index(engine, "skilllink", "evidence_id")
    _ensure_index(engine, "skilllink", "skill_id")
    _ensure_index(engine, "education", "evidence_id")
    _ensure_index(engine, "employment", "evidence_id")
    _ensure_index(engine, "project", "employment_id")
    _ensure_index(engine, "project", "evidence_id")
    _ensure_index(engine, "portfolioitem", "project_id")
    _ensure_index(engine, "portfoliolink", "portfolio_item_id")
    _ensure_index(engine, "portfoliofile", "portfolio_item_id")
    _ensure_index(engine, "learningactivity", "evidence_id")
    _ensure_index(engine, "consultmessage", "session_id")
    _ensure_search_index(engine)
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
