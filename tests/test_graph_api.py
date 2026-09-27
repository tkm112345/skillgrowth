from app.models import EvidenceEntry, LearningActivity, Skill, SkillLink


def _node_ids(nodes):
    return {n["id"] for n in nodes}


def _edge_pairs(edges):
    return {(e["source"], e["target"]) for e in edges}


def test_certification_backed_skill_appears_with_edge(client, session):
    skill = Skill(name="AWS", category="技術")
    session.add(skill)
    session.commit()
    session.refresh(skill)

    entry = EvidenceEntry(source_type="certification", raw_input="AWS SAA passed")
    session.add(entry)
    session.commit()
    session.refresh(entry)

    cert = LearningActivity(activity_type="certification", title="AWS SAA", evidence_id=entry.id)
    session.add(cert)
    session.commit()
    session.refresh(cert)

    session.add(SkillLink(evidence_id=entry.id, skill_id=skill.id, mention_text="AWS"))
    session.commit()

    resp = client.get("/api/graph")
    assert resp.status_code == 200
    data = resp.json()

    assert f"skill:{skill.id}" in _node_ids(data["nodes"])
    assert f"learning_activity:{cert.id}" in _node_ids(data["nodes"])
    assert (f"skill:{skill.id}", f"learning_activity:{cert.id}") in _edge_pairs(data["edges"])


def test_non_certification_activity_and_checkins_are_excluded(client, session):
    skill = Skill(name="Python", category="技術")
    session.add(skill)
    session.commit()
    session.refresh(skill)

    reading_entry = EvidenceEntry(source_type="learning_activity", raw_input="Read a book")
    session.add(reading_entry)
    session.commit()
    session.refresh(reading_entry)
    reading = LearningActivity(activity_type="Reading", title="Some book", evidence_id=reading_entry.id)
    session.add(reading)
    session.commit()
    session.refresh(reading)
    session.add(SkillLink(evidence_id=reading_entry.id, skill_id=skill.id, mention_text="Python"))

    checkin_entry = EvidenceEntry(source_type="checkin", raw_input="Worked on Python today")
    session.add(checkin_entry)
    session.commit()
    session.refresh(checkin_entry)
    session.add(SkillLink(evidence_id=checkin_entry.id, skill_id=skill.id, mention_text="Python"))
    session.commit()

    resp = client.get("/api/graph")
    assert resp.status_code == 200
    data = resp.json()

    node_ids = _node_ids(data["nodes"])
    assert f"learning_activity:{reading.id}" not in node_ids
    assert not any(e["source"] == f"skill:{skill.id}" for e in data["edges"])


def test_project_links_to_employment_and_portfolio_item(client):
    employment = client.post("/api/profile/employment", json={"company": "Acme"}).json()["employment"]
    company_project = client.post(
        "/api/profile/projects", json={"title": "Internal tool", "employment_id": employment["id"]}
    ).json()["project"]
    standalone_project = client.post("/api/profile/projects", json={"title": "Side project"}).json()["project"]
    portfolio_item = client.post(
        "/api/portfolio", json={"title": "Showcase", "description": "", "project_id": standalone_project["id"]}
    ).json()

    resp = client.get("/api/graph")
    assert resp.status_code == 200
    edges = _edge_pairs(resp.json()["edges"])
    assert (f"employment:{employment['id']}", f"project:{company_project['id']}") in edges
    assert (f"project:{standalone_project['id']}", f"portfolio_item:{portfolio_item['id']}") in edges
