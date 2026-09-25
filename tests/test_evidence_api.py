from datetime import datetime, timezone

from app import llm
from app.models import EvidenceEntry


def _enable_skill_extraction(client):
    client.put(
        "/api/settings",
        json={
            "openai_base_url": "https://api.openai.com/v1",
            "openai_api_key": "test-key",
            "llm_model": "gpt-4o-mini",
            "llm_vision_model": "gpt-4o-mini",
            "skill_extraction_enabled": True,
        },
    )


def test_add_text_evidence_links_extracted_skills(client, monkeypatch):
    _enable_skill_extraction(client)

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
    _enable_skill_extraction(client)
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


def test_list_evidence_months_groups_by_year_month(client, session):
    session.add(
        EvidenceEntry(source_type="checkin", raw_input="a", created_at=datetime(2024, 1, 5, tzinfo=timezone.utc))
    )
    session.add(
        EvidenceEntry(source_type="checkin", raw_input="b", created_at=datetime(2024, 1, 20, tzinfo=timezone.utc))
    )
    session.add(
        EvidenceEntry(source_type="checkin", raw_input="c", created_at=datetime(2024, 3, 1, tzinfo=timezone.utc))
    )
    session.commit()

    resp = client.get("/api/evidence/months")
    assert resp.status_code == 200
    assert resp.json() == [
        {"year": 2024, "month": 3, "count": 1},
        {"year": 2024, "month": 1, "count": 2},
    ]


def test_list_evidence_filters_by_year_and_month(client, session):
    session.add(
        EvidenceEntry(source_type="checkin", raw_input="jan", created_at=datetime(2024, 1, 5, tzinfo=timezone.utc))
    )
    session.add(
        EvidenceEntry(source_type="checkin", raw_input="mar", created_at=datetime(2024, 3, 1, tzinfo=timezone.utc))
    )
    session.commit()

    body = client.get("/api/evidence?year=2024&month=1").json()
    assert [e["raw_input"] for e in body] == ["jan"]


def test_add_image_evidence_over_limit_is_rejected(client):
    oversized = b"x" * (10 * 1024 * 1024 + 1)
    resp = client.post(
        "/api/evidence/image",
        files={"file": ("big.png", oversized, "image/png")},
        data={"source_type": "certification"},
    )
    assert resp.status_code == 400

    assert client.get("/api/evidence").json() == []


def test_llm_failure_surfaces_as_502_with_clear_detail(client, monkeypatch):
    _enable_skill_extraction(client)

    def fake_extract(text, existing_skills, settings):
        raise llm.LLMRequestError("Incorrect API key provided")

    monkeypatch.setattr(llm, "extract_and_match_text", fake_extract)

    resp = client.post("/api/evidence/text", json={"source_type": "checkin", "text": "anything"})
    assert resp.status_code == 502
    assert "Incorrect API key provided" in resp.json()["detail"]
