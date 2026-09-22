import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from starlette.testclient import TestClient

from app import db as db_module
from app.models import Settings


@pytest.fixture
def engine():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def session(engine):
    with Session(engine, expire_on_commit=False) as s:
        s.add(Settings(id=1))
        s.commit()
        yield s


@pytest.fixture
def client(engine, monkeypatch):
    monkeypatch.setattr(db_module, "init_db", lambda: None)

    def get_session_override():
        with Session(engine, expire_on_commit=False) as s:
            yield s

    with Session(engine) as s:
        s.add(Settings(id=1))
        s.commit()

    from app.main import app

    app.dependency_overrides[db_module.get_session] = get_session_override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
