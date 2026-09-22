def test_create_session_and_list(client):
    created = client.post("/api/consult/sessions").json()
    assert created["title"] == ""

    resp = client.get("/api/consult/sessions")
    assert resp.status_code == 200
    assert [s["id"] for s in resp.json()] == [created["id"]]


def test_send_message_persists_user_message_even_if_reply_fails(client, monkeypatch):
    from app import llm

    def boom(*args, **kwargs):
        raise llm.LLMRequestError("no api key")

    monkeypatch.setattr(llm, "career_consult_reply", boom)

    created = client.post("/api/consult/sessions").json()
    resp = client.post(f"/api/consult/sessions/{created['id']}/messages", json={"content": "How am I doing?"})
    assert resp.status_code == 502

    messages = client.get(f"/api/consult/sessions/{created['id']}/messages").json()
    assert len(messages) == 1
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "How am I doing?"


def test_send_message_calls_llm_with_full_history_and_context(client, monkeypatch):
    from app import llm

    client.post("/api/skills", json={"name": "Python", "category": "技術"})
    client.put("/api/vision", json={"content": "Become a staff engineer."})

    seen = {}

    def fake_reply(messages, context, locale, settings):
        seen["messages"] = messages
        seen["context"] = context
        seen["locale"] = locale
        return "Here's my advice."

    monkeypatch.setattr(llm, "career_consult_reply", fake_reply)

    created = client.post("/api/consult/sessions").json()
    resp = client.post(
        f"/api/consult/sessions/{created['id']}/messages",
        json={"content": "How am I doing?", "locale": "en"},
    )
    assert resp.status_code == 200
    assert resp.json()["role"] == "assistant"
    assert resp.json()["content"] == "Here's my advice."

    assert seen["messages"] == [{"role": "user", "content": "How am I doing?"}]
    assert "Become a staff engineer." in seen["context"]
    assert "Python" in seen["context"]
    assert seen["locale"] == "en"

    # The session's title is set from the first message, and both messages
    # (user + assistant) are now in history.
    session = client.get("/api/consult/sessions").json()[0]
    assert session["title"] == "How am I doing?"

    messages = client.get(f"/api/consult/sessions/{created['id']}/messages").json()
    assert [m["role"] for m in messages] == ["user", "assistant"]


def test_second_message_includes_prior_turns_in_history(client, monkeypatch):
    from app import llm

    seen_histories = []

    def fake_reply(messages, context, locale, settings):
        seen_histories.append([m["content"] for m in messages])
        return "ok"

    monkeypatch.setattr(llm, "career_consult_reply", fake_reply)

    created = client.post("/api/consult/sessions").json()
    client.post(f"/api/consult/sessions/{created['id']}/messages", json={"content": "first"})
    client.post(f"/api/consult/sessions/{created['id']}/messages", json={"content": "second"})

    assert seen_histories[0] == ["first"]
    assert seen_histories[1] == ["first", "ok", "second"]


def test_delete_session_removes_its_messages(client, monkeypatch):
    from app import llm

    monkeypatch.setattr(llm, "career_consult_reply", lambda *a, **k: "ok")

    created = client.post("/api/consult/sessions").json()
    client.post(f"/api/consult/sessions/{created['id']}/messages", json={"content": "hi"})

    resp = client.delete(f"/api/consult/sessions/{created['id']}")
    assert resp.status_code == 200
    assert client.get("/api/consult/sessions").json() == []


def test_get_session_detail(client):
    created = client.post("/api/consult/sessions").json()
    resp = client.get(f"/api/consult/sessions/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == created["id"]


def test_get_session_detail_missing_returns_404(client):
    resp = client.get("/api/consult/sessions/does-not-exist")
    assert resp.status_code == 404


def test_send_message_to_missing_session_returns_404(client):
    resp = client.post("/api/consult/sessions/does-not-exist/messages", json={"content": "hi"})
    assert resp.status_code == 404
