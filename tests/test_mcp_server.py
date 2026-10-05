import base64
import json

from fastapi import FastAPI
from starlette.testclient import TestClient

from app.basic_auth import setup_basic_auth
from app.mcp_server import setup_mcp


def _app_with_whitelisted_and_other_route():
    app = FastAPI()

    @app.get("/ping", operation_id="list_bookmarks")
    def ping():
        return {"ok": True}

    @app.get("/other", operation_id="not_in_whitelist")
    def other():
        return {"ok": True}

    return app


def _mcp_initialize(client: TestClient) -> dict:
    """Minimal MCP Streamable HTTP handshake: initialize, then
    notifications/initialized. Returns headers (including the session id)
    to reuse on follow-up requests."""
    resp = client.post(
        "/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "t", "version": "0"},
            },
        },
        headers={"Accept": "application/json, text/event-stream"},
    )
    assert resp.status_code == 200, resp.text
    headers = {"Accept": "application/json, text/event-stream", "mcp-session-id": resp.headers["mcp-session-id"]}
    client.post("/mcp", json={"jsonrpc": "2.0", "method": "notifications/initialized"}, headers=headers)
    return headers


def test_mcp_disabled_by_default_when_env_var_unset(monkeypatch):
    monkeypatch.delenv("SKILLGROWTH_MCP_ENABLED", raising=False)
    app = _app_with_whitelisted_and_other_route()
    setup_mcp(app)

    assert not any(getattr(r, "path", "").startswith("/mcp") for r in app.routes)


def test_mcp_mounts_when_enabled(monkeypatch):
    monkeypatch.setenv("SKILLGROWTH_MCP_ENABLED", "1")
    app = _app_with_whitelisted_and_other_route()
    setup_mcp(app)

    assert any(getattr(r, "path", "").startswith("/mcp") for r in app.routes)
    with TestClient(app) as client:
        # A plain GET without declaring SSE support is the documented
        # Streamable HTTP rejection — a 406, not a 404 — confirming the
        # endpoint is live and speaking the MCP protocol.
        resp = client.get("/mcp")
        assert resp.status_code == 406


def test_mcp_only_exposes_whitelisted_operations(monkeypatch):
    monkeypatch.setenv("SKILLGROWTH_MCP_ENABLED", "1")
    app = _app_with_whitelisted_and_other_route()
    setup_mcp(app)

    with TestClient(app) as client:
        headers = _mcp_initialize(client)
        resp = client.post("/mcp", json={"jsonrpc": "2.0", "id": 2, "method": "tools/list"}, headers=headers)
        tool_names = [t["name"] for t in json.loads(resp.text)["result"]["tools"]]

    assert tool_names == ["list_bookmarks"]


def test_mcp_protected_by_basic_auth_when_both_enabled(monkeypatch):
    monkeypatch.setenv("SKILLGROWTH_MCP_ENABLED", "1")
    monkeypatch.setenv("SKILLGROWTH_BASIC_AUTH_USER", "alice")
    monkeypatch.setenv("SKILLGROWTH_BASIC_AUTH_PASS", "secret")
    app = _app_with_whitelisted_and_other_route()
    # Mirrors app/main.py's order: basic auth is set up first, routers and
    # the MCP mount come after — the Basic Auth middleware wraps the app's
    # router object itself, so it covers routes added afterwards too.
    setup_basic_auth(app)
    setup_mcp(app)

    with TestClient(app) as client:
        unauthenticated = client.get("/mcp")
        assert unauthenticated.status_code == 401

        token = base64.b64encode(b"alice:secret").decode()
        authenticated = client.get("/mcp", headers={"Authorization": f"Basic {token}"})
        # Past the auth gate: falls through to the same 406 an
        # unauthenticated-but-plain-GET gets in test_mcp_mounts_when_enabled.
        assert authenticated.status_code == 406
