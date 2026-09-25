def test_default_types_seeded(client):
    types = client.get("/api/learning/types").json()
    assert len(types) == 5

    protected = [t for t in types if t["is_protected"]]
    assert len(protected) == 1
    assert protected[0]["label"] == "certification"

    other_labels = {t["label"] for t in types if not t["is_protected"]}
    assert other_labels == {"Reading", "Talk given", "Talk attended", "Other"}


def test_create_custom_type(client):
    resp = client.post("/api/learning/types", json={"label": "Side project"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["label"] == "Side project"
    assert body["is_protected"] is False
    assert body["translation_key"] is None

    types = client.get("/api/learning/types").json()
    assert "Side project" in [t["label"] for t in types]


def test_create_rejects_empty_label(client):
    resp = client.post("/api/learning/types", json={"label": "   "})
    assert resp.status_code == 400


def test_create_rejects_duplicate_label_case_insensitive(client):
    resp = client.post("/api/learning/types", json={"label": "reading"})
    assert resp.status_code == 400

    resp = client.post("/api/learning/types", json={"label": "Certification"})
    assert resp.status_code == 400


def test_rename_custom_type(client):
    created = client.post("/api/learning/types", json={"label": "Side project"}).json()

    resp = client.put(f"/api/learning/types/{created['id']}", json={"label": "Weekend project"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["label"] == "Weekend project"
    assert body["translation_key"] is None


def test_rename_rejects_protected_type(client):
    types = client.get("/api/learning/types").json()
    protected = next(t for t in types if t["is_protected"])

    resp = client.put(f"/api/learning/types/{protected['id']}", json={"label": "Something else"})
    assert resp.status_code == 400

    types_after = client.get("/api/learning/types").json()
    assert next(t for t in types_after if t["id"] == protected["id"])["label"] == "certification"


def test_delete_custom_type(client):
    created = client.post("/api/learning/types", json={"label": "Side project"}).json()

    resp = client.delete(f"/api/learning/types/{created['id']}")
    assert resp.status_code == 200

    labels = [t["label"] for t in client.get("/api/learning/types").json()]
    assert "Side project" not in labels


def test_delete_rejects_protected_type(client):
    types = client.get("/api/learning/types").json()
    protected = next(t for t in types if t["is_protected"])

    resp = client.delete(f"/api/learning/types/{protected['id']}")
    assert resp.status_code == 400

    labels = [t["label"] for t in client.get("/api/learning/types").json()]
    assert "certification" in labels


def test_delete_does_not_affect_existing_activities(client):
    created = client.post("/api/learning/types", json={"label": "Side project"}).json()
    client.post("/api/learning", json={"activity_type": "Side project", "title": "Built a thing"})

    client.delete(f"/api/learning/types/{created['id']}")

    activities = client.get("/api/learning").json()
    assert [a["activity_type"] for a in activities] == ["Side project"]
