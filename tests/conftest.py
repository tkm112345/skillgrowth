from io import BytesIO

import pytest
from docx import Document
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool
from starlette.testclient import TestClient

from app import db as db_module
from app.models import ActivityType, Settings


@pytest.fixture
def engine():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def session(engine):
    with Session(engine, expire_on_commit=False) as s:
        if s.get(Settings, 1) is None:
            s.add(Settings(id=1))
            s.commit()
        if s.exec(select(ActivityType)).first() is None:
            s.add_all(db_module.default_activity_types())
            s.commit()
        yield s


@pytest.fixture
def client(engine, monkeypatch):
    monkeypatch.setattr(db_module, "init_db", lambda: None)

    def get_session_override():
        with Session(engine, expire_on_commit=False) as s:
            yield s

    with Session(engine) as s:
        if s.get(Settings, 1) is None:
            s.add(Settings(id=1))
        if s.exec(select(ActivityType)).first() is None:
            s.add_all(db_module.default_activity_types())
        s.commit()

    from app.main import app

    app.dependency_overrides[db_module.get_session] = get_session_override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def sample_docx_bytes():
    """A minimal .docx with one tag per resume section, for exercising the
    Word-template renderer without checking a binary fixture into the repo."""

    def build() -> bytes:
        doc = Document()
        for tag in ("self_pr", "employment", "projects", "education", "skills", "certifications"):
            doc.add_paragraph("{{p " + tag + " }}")
        buf = BytesIO()
        doc.save(buf)
        return buf.getvalue()

    return build
