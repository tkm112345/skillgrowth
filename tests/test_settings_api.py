def test_test_settings_reports_success(client, monkeypatch):
    from app import llm

    monkeypatch.setattr(llm, "test_connection", lambda settings: {"ok": True, "message": "ok"})

    resp = client.post(
        "/api/settings/test",
        json={
            "openai_base_url": "https://api.openai.com/v1",
            "openai_api_key": "test-key",
            "llm_model": "gpt-4o-mini",
            "llm_vision_model": "gpt-4o-mini",
        },
    )
    assert resp.status_code == 200
    assert resp.json() == {"ok": True, "message": "ok"}


def test_test_settings_reports_failure(client, monkeypatch):
    from app import llm

    monkeypatch.setattr(llm, "test_connection", lambda settings: {"ok": False, "message": "invalid api key"})

    resp = client.post(
        "/api/settings/test",
        json={
            "openai_base_url": "https://api.openai.com/v1",
            "openai_api_key": "bad-key",
            "llm_model": "gpt-4o-mini",
            "llm_vision_model": "gpt-4o-mini",
        },
    )
    assert resp.status_code == 200
    assert resp.json()["ok"] is False
