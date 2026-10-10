def test_get_vision_returns_empty_default_when_unset(client):
    resp = client.get("/api/vision")
    assert resp.status_code == 200
    assert resp.json()["content"] == ""
    assert resp.json()["updated_at"] is None
    assert resp.json()["include_in_resume"] is False


def test_resume_inclusion_defaults_off_and_can_be_toggled(client):
    resp = client.put("/api/vision/resume-inclusion", json={"include_in_resume": True})
    assert resp.status_code == 200
    assert resp.json()["include_in_resume"] is True
    assert client.get("/api/vision").json()["include_in_resume"] is True

    client.put("/api/vision/resume-inclusion", json={"include_in_resume": False})
    assert client.get("/api/vision").json()["include_in_resume"] is False


def test_resume_inclusion_toggle_does_not_touch_content(client):
    client.put("/api/vision", json={"content": "Go deep on infra."})
    client.put("/api/vision/resume-inclusion", json={"include_in_resume": True})
    assert client.get("/api/vision").json()["content"] == "Go deep on infra."


def test_get_vision_returns_real_timestamp_only_after_save(client):
    client.put("/api/vision", json={"content": "Go deep on infra."})
    resp = client.get("/api/vision")
    assert resp.json()["updated_at"] is not None


def test_update_vision_persists_and_overwrites_in_place(client):
    resp = client.put("/api/vision", json={"content": "Grow into a staff-level generalist."})
    assert resp.status_code == 200
    assert resp.json()["content"] == "Grow into a staff-level generalist."

    resp = client.put("/api/vision", json={"content": "Go deep on infra instead."})
    assert resp.json()["content"] == "Go deep on infra instead."

    resp = client.get("/api/vision")
    assert resp.json()["content"] == "Go deep on infra instead."
