def test_get_vision_returns_empty_default_when_unset(client):
    resp = client.get("/api/vision")
    assert resp.status_code == 200
    assert resp.json()["content"] == ""


def test_update_vision_persists_and_overwrites_in_place(client):
    resp = client.put("/api/vision", json={"content": "Grow into a staff-level generalist."})
    assert resp.status_code == 200
    assert resp.json()["content"] == "Grow into a staff-level generalist."

    resp = client.put("/api/vision", json={"content": "Go deep on infra instead."})
    assert resp.json()["content"] == "Go deep on infra instead."

    resp = client.get("/api/vision")
    assert resp.json()["content"] == "Go deep on infra instead."
