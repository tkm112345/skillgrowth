def test_add_link_creates_and_lists(client):
    resp = client.post("/api/profile/links", json={"label": "GitHub", "url": "https://github.com/example"})
    assert resp.status_code == 200
    assert resp.json()["label"] == "GitHub"

    resp = client.get("/api/profile/links")
    assert [link["label"] for link in resp.json()] == ["GitHub"]


def test_delete_link(client):
    created = client.post(
        "/api/profile/links", json={"label": "X", "url": "https://x.com/example"}
    ).json()

    resp = client.delete(f"/api/profile/links/{created['id']}")
    assert resp.status_code == 200

    resp = client.get("/api/profile/links")
    assert resp.json() == []
