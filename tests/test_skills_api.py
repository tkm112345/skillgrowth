def test_add_skill_creates_and_lists(client):
    resp = client.post("/api/skills", json={"name": "Python", "category": "技術"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "Python"

    resp = client.get("/api/skills")
    assert resp.status_code == 200
    names = [s["name"] for s in resp.json()]
    assert names == ["Python"]


def test_add_skill_is_case_insensitive_dedup(client):
    client.post("/api/skills", json={"name": "Python", "category": "技術"})
    client.post("/api/skills", json={"name": "python", "category": "技術"})

    resp = client.get("/api/skills")
    assert len(resp.json()) == 1


def test_delete_skill(client):
    created = client.post("/api/skills", json={"name": "Python", "category": "技術"}).json()

    resp = client.delete(f"/api/skills/{created['id']}")
    assert resp.status_code == 200

    resp = client.get("/api/skills")
    assert resp.json() == []
