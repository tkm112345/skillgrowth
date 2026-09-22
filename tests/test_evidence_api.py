from app import llm


def test_add_text_evidence_links_extracted_skills(client, monkeypatch):
    def fake_extract(text, existing_skills, settings):
        return [{"mention_text": text, "skill_id": None, "name": "Python", "category": "技術"}]

    monkeypatch.setattr(llm, "extract_and_match_text", fake_extract)

    resp = client.post("/api/evidence/text", json={"source_type": "checkin", "text": "did some Python work"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["evidence"]["source_type"] == "checkin"
    assert len(body["linked_skills"]) == 1
    assert body["linked_skills"][0]["name"] == "Python"

    skills = client.get("/api/skills").json()
    assert [s["name"] for s in skills] == ["Python"]

    evidence = client.get("/api/evidence").json()
    assert len(evidence) == 1


def test_second_checkin_reuses_matched_skill(client, monkeypatch):
    calls = {"n": 0}

    def fake_extract(text, existing_skills, settings):
        calls["n"] += 1
        if existing_skills:
            return [{"mention_text": text, "skill_id": existing_skills[0]["id"], "name": None, "category": None}]
        return [{"mention_text": text, "skill_id": None, "name": "Python", "category": "技術"}]

    monkeypatch.setattr(llm, "extract_and_match_text", fake_extract)

    client.post("/api/evidence/text", json={"source_type": "checkin", "text": "Python again"})
    client.post("/api/evidence/text", json={"source_type": "checkin", "text": "more Python"})

    skills = client.get("/api/skills").json()
    assert len(skills) == 1
    assert skills[0]["evidence_count"] == 2
