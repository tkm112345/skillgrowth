def test_consult_custom_instructions_round_trips(client):
    resp = client.put(
        "/api/settings",
        json={
            "openai_base_url": "https://api.openai.com/v1",
            "openai_api_key": "key",
            "llm_model": "gpt-4o-mini",
            "llm_vision_model": "gpt-4o-mini",
            "consult_custom_instructions": "Always answer in a blunt, no-nonsense tone.",
        },
    )
    assert resp.status_code == 200
    assert resp.json()["consult_custom_instructions"] == "Always answer in a blunt, no-nonsense tone."

    assert client.get("/api/settings").json()["consult_custom_instructions"] == (
        "Always answer in a blunt, no-nonsense tone."
    )


def test_get_settings_masks_api_key(client):
    client.put(
        "/api/settings",
        json={
            "openai_base_url": "https://api.openai.com/v1",
            "openai_api_key": "real-secret-key",
            "llm_model": "gpt-4o-mini",
            "llm_vision_model": "gpt-4o-mini",
        },
    )

    resp = client.get("/api/settings")
    assert resp.status_code == 200
    assert resp.json()["openai_api_key"] == "••••••••"


def test_put_settings_with_masked_key_keeps_existing_key(client, monkeypatch):
    from app import llm

    client.put(
        "/api/settings",
        json={
            "openai_base_url": "https://api.openai.com/v1",
            "openai_api_key": "real-secret-key",
            "llm_model": "gpt-4o-mini",
            "llm_vision_model": "gpt-4o-mini",
        },
    )

    client.put(
        "/api/settings",
        json={
            "openai_base_url": "https://api.openai.com/v1",
            "openai_api_key": "••••••••",
            "llm_model": "gpt-4o",
            "llm_vision_model": "gpt-4o-mini",
        },
    )

    seen = {}

    def fake_test_connection(settings):
        seen["key"] = settings.openai_api_key
        return {"ok": True, "message": "ok"}

    monkeypatch.setattr(llm, "test_connection", fake_test_connection)
    client.post(
        "/api/settings/test",
        json={
            "openai_base_url": "https://api.openai.com/v1",
            "openai_api_key": "••••••••",
            "llm_model": "gpt-4o",
            "llm_vision_model": "gpt-4o-mini",
        },
    )
    assert seen["key"] == "real-secret-key"


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
