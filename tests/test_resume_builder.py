from app.models import Education, Employment, Skill
from app.resume_builder import build_resume_markdown


def test_generate_export_does_not_require_llm(client, monkeypatch):
    """Resume generation must never touch the LLM — it's pure template
    filling from structured data. Breaking the shared low-level LLM call
    here proves the endpoint never reaches it."""
    from app import llm

    def boom(*args, **kwargs):
        raise AssertionError("resume generation should not call the LLM")

    monkeypatch.setattr(llm, "_complete", boom)

    client.post("/api/skills", json={"name": "Python", "category": "技術"})
    resp = client.post("/api/export")
    assert resp.status_code == 200
    assert "Python" in resp.json()["content"]


def test_resume_sections_appear_in_fixed_order(session):
    session.add(Education(school="Test U", degree="B.S.", major="CS"))
    session.add(Employment(company="Acme", role="Engineer"))
    session.add(Skill(name="Python", category="技術"))
    session.commit()

    content = build_resume_markdown(session)

    work_idx = content.index("## Work History")
    education_idx = content.index("## Education")
    skills_idx = content.index("## Skills")
    assert work_idx < education_idx < skills_idx
    assert "Acme" in content
    assert "Test U" in content
    assert "Python" in content


def test_resume_omits_empty_sections(session):
    content = build_resume_markdown(session)
    assert "## Self PR" not in content
    assert "## Work History" not in content
    assert content.strip() == "# Resume"
