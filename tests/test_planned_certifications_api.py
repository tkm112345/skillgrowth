def test_add_planned_certification_creates_and_lists(client):
    resp = client.post(
        "/api/planned-certifications",
        json={"title": "AWS SAA", "status": "planned", "target_date": "2026-12-01", "notes": "study plan"},
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "AWS SAA"

    resp = client.get("/api/planned-certifications")
    assert [p["title"] for p in resp.json()] == ["AWS SAA"]


def test_add_planned_certification_rejects_invalid_status(client):
    resp = client.post("/api/planned-certifications", json={"title": "AWS SAA", "status": "done"})
    assert resp.status_code == 400


def test_add_planned_certification_requires_title(client):
    resp = client.post("/api/planned-certifications", json={"title": "", "status": "considering"})
    assert resp.status_code == 400


def test_update_planned_certification(client):
    created = client.post("/api/planned-certifications", json={"title": "AWS SAA", "status": "considering"}).json()

    resp = client.put(
        f"/api/planned-certifications/{created['id']}",
        json={"title": "AWS SAP", "status": "planned", "target_date": "2027-01-01", "notes": "upgraded"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["title"] == "AWS SAP"
    assert body["status"] == "planned"
    assert body["notes"] == "upgraded"


def test_update_planned_certification_missing_id_returns_404(client):
    resp = client.put("/api/planned-certifications/does-not-exist", json={"title": "X", "status": "considering"})
    assert resp.status_code == 404


def test_delete_planned_certification(client):
    created = client.post("/api/planned-certifications", json={"title": "AWS SAA", "status": "considering"}).json()

    resp = client.delete(f"/api/planned-certifications/{created['id']}")
    assert resp.status_code == 200
    assert client.get("/api/planned-certifications").json() == []


def test_promote_creates_learning_activity_and_deletes_planned(client):
    created = client.post(
        "/api/planned-certifications",
        json={"title": "AWS SAA", "status": "planned", "notes": "study plan"},
    ).json()

    resp = client.post(f"/api/planned-certifications/{created['id']}/promote", json={"activity_date": "2026-10-05"})
    assert resp.status_code == 200
    activity = resp.json()
    assert activity["activity_type"] == "certification"
    assert activity["title"] == "AWS SAA"
    assert activity["activity_date"] == "2026-10-05"

    assert client.get("/api/planned-certifications").json() == []

    learning = client.get("/api/learning").json()
    assert [a["title"] for a in learning] == ["AWS SAA"]

    evidence = client.get("/api/evidence").json()
    assert len(evidence) == 1
    assert evidence[0]["source_type"] == "certification"


def test_promote_missing_id_returns_404(client):
    resp = client.post("/api/planned-certifications/does-not-exist/promote", json={})
    assert resp.status_code == 404
