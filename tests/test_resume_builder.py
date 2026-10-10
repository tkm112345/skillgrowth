from sqlmodel import select

from app.models import (
    ActivityType,
    CareerGoal,
    CareerVision,
    Education,
    Employment,
    ExternalLink,
    LearningActivity,
    PersonalValues,
    PortfolioItem,
    PortfolioLink,
    Skill,
)
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


def test_external_link_included_only_when_toggled_on(session):
    session.add(ExternalLink(label="GitHub", url="https://github.com/example", include_in_resume=False))
    session.commit()
    assert "## Activities & Links" not in build_resume_markdown(session)

    link = session.exec(select(ExternalLink)).first()
    link.include_in_resume = True
    session.add(link)
    session.commit()

    content = build_resume_markdown(session)
    assert "## Activities & Links" in content
    assert "github.com/example" in content


def test_talk_shown_only_when_activity_type_toggled_on(session):
    talk_type = ActivityType(label="Talk given", include_in_resume=False)
    session.add(talk_type)
    session.add(LearningActivity(activity_type="Talk given", title="Conference keynote"))
    session.commit()
    assert "Conference keynote" not in build_resume_markdown(session)

    talk_type.include_in_resume = True
    session.add(talk_type)
    session.commit()

    content = build_resume_markdown(session)
    assert "## Activities & Links" in content
    assert "Conference keynote" in content


def test_certification_never_appears_in_activities_section(session):
    cert_type = session.exec(select(ActivityType).where(ActivityType.label == "certification")).first()
    cert_type.include_in_resume = True  # even if someone flips this on
    session.add(cert_type)
    session.add(LearningActivity(activity_type="certification", title="AWS SAA"))
    session.commit()

    content = build_resume_markdown(session)
    # It still shows up in the dedicated Certifications section...
    assert "## Certifications" in content
    assert "AWS SAA" in content
    # ...but Activities & Links stays empty and omitted (no other eligible data).
    assert "## Activities & Links" not in content


def test_portfolio_item_included_only_when_toggled_on(session):
    item = PortfolioItem(title="Side Project", description="A thing I built", include_in_resume=False)
    session.add(item)
    session.commit()
    session.add(PortfolioLink(portfolio_item_id=item.id, label="Repo", url="https://example.com/repo"))
    session.commit()
    assert "Side Project" not in build_resume_markdown(session)

    item.include_in_resume = True
    session.add(item)
    session.commit()

    content = build_resume_markdown(session)
    assert "## Activities & Links" in content
    assert "Side Project" in content
    assert "example.com/repo" in content


def test_personal_values_defaults_to_shown_and_appears_last(session):
    session.add(PersonalValues(id=1, content="世界をちょっとだけ良くしたい"))
    session.add(LearningActivity(activity_type="certification", title="AWS SAA"))
    session.commit()

    content = build_resume_markdown(session)
    assert "## Personal Values" in content
    assert "世界をちょっとだけ良くしたい" in content
    assert content.index("## Certifications") < content.index("## Personal Values")


def test_personal_values_omitted_when_toggled_off(session):
    session.add(PersonalValues(id=1, content="世界をちょっとだけ良くしたい", include_in_resume=False))
    session.commit()
    assert "## Personal Values" not in build_resume_markdown(session)
