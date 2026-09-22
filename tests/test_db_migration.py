from sqlmodel import Session, create_engine, text

from app.db import _ensure_column


def test_ensure_column_adds_missing_column_to_existing_table():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    with engine.connect() as conn:
        conn.exec_driver_sql("CREATE TABLE exportsnapshot (id TEXT PRIMARY KEY, content TEXT)")
        conn.commit()

    _ensure_column(engine, "exportsnapshot", "edited_at", "TIMESTAMP")

    with Session(engine) as session:
        session.exec(
            text("INSERT INTO exportsnapshot (id, content, edited_at) VALUES ('x', 'y', NULL)")
        )
        session.commit()
        row = session.exec(text("SELECT edited_at FROM exportsnapshot WHERE id = 'x'")).first()
        assert row[0] is None


def test_ensure_column_is_a_no_op_when_column_already_exists():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    with engine.connect() as conn:
        conn.exec_driver_sql(
            "CREATE TABLE exportsnapshot (id TEXT PRIMARY KEY, content TEXT, edited_at TIMESTAMP)"
        )
        conn.commit()

    # Must not raise (e.g. a duplicate-column error) when called again.
    _ensure_column(engine, "exportsnapshot", "edited_at", "TIMESTAMP")
    _ensure_column(engine, "exportsnapshot", "edited_at", "TIMESTAMP")
