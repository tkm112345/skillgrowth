"""Integration test spanning evidence -> services -> skills -> resume_builder,
exercised against the real (in-memory) DB via the `client`/`session` fixtures
(see conftest.py) rather than any single router in isolation."""

from app import llm
from app.resume_builder import build_resume_markdown


def test_evidence_to_resume_flow(client, session, monkeypatch):
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

    def fake_extract(text, existing_skills, settings):
        return [{"mention_text": text, "skill_id": None, "name": "Python", "category": "技術"}]

    monkeypatch.setattr(llm, "extract_and_match_text", fake_extract)

    resp = client.post("/api/evidence/text", json={"source_type": "checkin", "text": "did some Python work"})
    assert resp.status_code == 200

    skills = client.get("/api/skills").json()
    assert len(skills) == 1
    skill = skills[0]
    assert skill["name"] == "Python"
    assert skill["include_in_resume"] is True

    content = build_resume_markdown(session)
    assert "Python" in content

    resp = client.put(f"/api/skills/{skill['id']}/resume-inclusion", json={"include_in_resume": False})
    assert resp.status_code == 200

    content = build_resume_markdown(session)
    assert "Python" not in content
