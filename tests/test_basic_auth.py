import base64

from fastapi import FastAPI
from starlette.testclient import TestClient

from app.basic_auth import _credentials_valid, setup_basic_auth


def _basic_header(user: str, password: str) -> dict:
    token = base64.b64encode(f"{user}:{password}".encode()).decode()
    return {"Authorization": f"Basic {token}"}


def test_credentials_valid_accepts_correct_user_and_password():
    assert _credentials_valid(_basic_header("alice", "secret")["Authorization"], "alice", "secret")


def test_credentials_valid_rejects_wrong_password():
    assert not _credentials_valid(_basic_header("alice", "wrong")["Authorization"], "alice", "secret")


def test_credentials_valid_rejects_missing_header():
    assert not _credentials_valid(None, "alice", "secret")


def test_credentials_valid_rejects_malformed_header():
    assert not _credentials_valid("Basic not-valid-base64!!", "alice", "secret")


def _app_with_ping_and_health():
    app = FastAPI()

    @app.get("/ping")
    def ping():
        return {"ok": True}

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    return app


def test_gate_disabled_when_env_vars_unset(monkeypatch):
    monkeypatch.delenv("SKILLGROWTH_BASIC_AUTH_USER", raising=False)
    monkeypatch.delenv("SKILLGROWTH_BASIC_AUTH_PASS", raising=False)
    app = _app_with_ping_and_health()
    setup_basic_auth(app)

    resp = TestClient(app).get("/ping")
    assert resp.status_code == 200


def test_gate_rejects_unauthenticated_request_when_enabled(monkeypatch):
    monkeypatch.setenv("SKILLGROWTH_BASIC_AUTH_USER", "alice")
    monkeypatch.setenv("SKILLGROWTH_BASIC_AUTH_PASS", "secret")
    app = _app_with_ping_and_health()
    setup_basic_auth(app)

    resp = TestClient(app).get("/ping")
    assert resp.status_code == 401


def test_gate_allows_correct_credentials(monkeypatch):
    monkeypatch.setenv("SKILLGROWTH_BASIC_AUTH_USER", "alice")
    monkeypatch.setenv("SKILLGROWTH_BASIC_AUTH_PASS", "secret")
    app = _app_with_ping_and_health()
    setup_basic_auth(app)

    resp = TestClient(app).get("/ping", headers=_basic_header("alice", "secret"))
    assert resp.status_code == 200


def test_gate_exempts_health_endpoint(monkeypatch):
    monkeypatch.setenv("SKILLGROWTH_BASIC_AUTH_USER", "alice")
    monkeypatch.setenv("SKILLGROWTH_BASIC_AUTH_PASS", "secret")
    app = _app_with_ping_and_health()
    setup_basic_auth(app)

    resp = TestClient(app).get("/api/health")
    assert resp.status_code == 200
