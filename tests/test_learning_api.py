def test_certification_activity_gets_certification_evidence_tag(client):
    client.post("/api/learning", json={"activity_type": "certification", "title": "AWS SAA"})

    evidence = client.get("/api/evidence").json()
    assert len(evidence) == 1
    assert evidence[0]["source_type"] == "certification"


def test_non_certification_activity_keeps_generic_learning_tag(client):
    client.post("/api/learning", json={"activity_type": "Reading", "title": "Some book"})

    evidence = client.get("/api/evidence").json()
    assert len(evidence) == 1
    assert evidence[0]["source_type"] == "learning_activity"


def test_new_activity_defaults_to_included_in_resume(client):
    created = client.post("/api/learning", json={"activity_type": "certification", "title": "AWS SAA"}).json()
    assert created["activity"]["include_in_resume"] is True


def test_toggle_learning_resume_inclusion(client):
    created = client.post("/api/learning", json={"activity_type": "certification", "title": "AWS SAA"}).json()
    activity_id = created["activity"]["id"]

    resp = client.put(f"/api/learning/{activity_id}/resume-inclusion", json={"include_in_resume": False})
    assert resp.status_code == 200
    assert resp.json()["include_in_resume"] is False

    activities = client.get("/api/learning").json()
    assert activities[0]["include_in_resume"] is False


def test_toggle_learning_resume_inclusion_missing_id_returns_404(client):
    resp = client.put("/api/learning/does-not-exist/resume-inclusion", json={"include_in_resume": False})
    assert resp.status_code == 404
