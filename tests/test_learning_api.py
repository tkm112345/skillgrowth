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
