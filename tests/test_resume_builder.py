from app.models import CareerGoal, CareerVision, Education, Employment, LearningActivity, Skill
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


def test_certification_excluded_from_resume_when_include_in_resume_is_false(session):
    session.add(LearningActivity(activity_type="certification", title="Shown Cert"))
    session.add(LearningActivity(activity_type="certification", title="Hidden Cert", include_in_resume=False))
    session.commit()

    content = build_resume_markdown(session)
    assert "Shown Cert" in content
    assert "Hidden Cert" not in content


def test_vision_included_only_when_toggled_on(session):
    session.add(CareerVision(id=1, content="好きな価値観", include_in_resume=False))
    session.commit()
    assert "## Vision" not in build_resume_markdown(session)

    vision = session.get(CareerVision, 1)
    vision.include_in_resume = True
    session.add(vision)
    session.commit()

    content = build_resume_markdown(session)
    assert "## Vision" in content
    assert "好きな価値観" in content


def test_blank_vision_is_omitted_even_when_toggled_on(session):
    session.add(CareerVision(id=1, content="   ", include_in_resume=True))
    session.commit()
    assert "## Vision" not in build_resume_markdown(session)


def test_goals_included_only_when_toggled_on_per_horizon(session):
    session.add(CareerGoal(horizon="this_year", description="今年の目標", include_in_resume=True))
    session.add(CareerGoal(horizon="5_years", description="5年後の目標", include_in_resume=False))
    session.commit()

    content = build_resume_markdown(session)
    assert "## Career Goals" in content
    assert "今年の目標" in content
    assert "5年後の目標" not in content
