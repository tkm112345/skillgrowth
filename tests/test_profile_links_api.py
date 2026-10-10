def test_add_link_creates_and_lists(client):
    resp = client.post("/api/profile/links", json={"label": "GitHub", "url": "https://github.com/example"})
    assert resp.status_code == 200
    assert resp.json()["label"] == "GitHub"
    assert resp.json()["include_in_resume"] is False

    resp = client.get("/api/profile/links")
    assert [link["label"] for link in resp.json()] == ["GitHub"]


def test_resume_inclusion_defaults_off_and_can_be_toggled(client):
    created = client.post("/api/profile/links", json={"label": "GitHub", "url": "https://github.com/example"}).json()

    resp = client.put(f"/api/profile/links/{created['id']}/resume-inclusion", json={"include_in_resume": True})
    assert resp.status_code == 200
    assert resp.json()["include_in_resume"] is True

    links = client.get("/api/profile/links").json()
    assert links[0]["include_in_resume"] is True


def test_delete_link(client):
    created = client.post("/api/profile/links", json={"label": "X", "url": "https://x.com/example"}).json()

    resp = client.delete(f"/api/profile/links/{created['id']}")
    assert resp.status_code == 200

    resp = client.get("/api/profile/links")
    assert resp.json() == []
