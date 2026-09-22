from pathlib import Path

from sqlmodel import SQLModel, Session, create_engine

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)
UPLOAD_DIR = DATA_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

engine = create_engine(f"sqlite:///{DATA_DIR / 'skillgrowth.db'}")


def init_db() -> None:
    from app.models import Settings  # noqa: PLC0415 (avoid circular import at module load)

    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        if session.get(Settings, 1) is None:
            session.add(Settings(id=1))
            session.commit()


def get_session():
    with Session(engine) as session:
        yield session
