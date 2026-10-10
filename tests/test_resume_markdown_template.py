from app.models import CareerGoal, CareerVision, Education, Employment, Project, ResumeMdTemplate, SelfPR, Skill
from app.resume_markdown_template import render_resume_markdown_template


def test_render_fills_tags_from_structured_data(session, tmp_path, sample_md_template_bytes):
    template_path = tmp_path / "template.md"
    template_path.write_bytes(sample_md_template_bytes())

    session.add(SelfPR(content="A short pitch", is_selected=True))
    session.add(CareerVision(id=1, content="My vision", include_in_resume=True))
    session.add(CareerGoal(horizon="this_year", description="This year's goal", include_in_resume=True))
    session.add(Employment(id="emp-1", company="Acme", role="Engineer"))
    session.add(Project(employment_id="emp-1", title="Widget launch", role="Lead"))
    session.add(Project(title="Side project", role="Solo"))
    session.add(Education(school="Test University", degree="B.S.", major="CS"))
    session.add(Skill(name="Python", category="技術"))
    session.commit()

    template = ResumeMdTemplate(name="Default", file_path=str(template_path))
    text = render_resume_markdown_template(session, template)

    assert "A short pitch" in text
    assert "My vision" in text
    assert "This year's goal" in text
    assert "Acme" in text
    assert "Widget launch" in text
    assert "Side project" in text
    assert "Test University" in text
    assert "Python" in text


def test_render_does_not_require_llm(session, tmp_path, sample_md_template_bytes, monkeypatch):
    from app import llm

    def boom(*args, **kwargs):
        raise AssertionError("resume markdown template generation should not call the LLM")

    monkeypatch.setattr(llm, "_complete", boom)

    template_path = tmp_path / "template.md"
    template_path.write_bytes(sample_md_template_bytes())
    template = ResumeMdTemplate(name="Default", file_path=str(template_path))

    render_resume_markdown_template(session, template)  # must not raise


def test_section_format_table_renders_a_markdown_table(session, tmp_path, sample_md_template_bytes):
    template_path = tmp_path / "template.md"
    template_path.write_bytes(sample_md_template_bytes())

    session.add(Skill(name="Python", category="技術"))
    session.commit()

    bullet_template = ResumeMdTemplate(name="Bullet", file_path=str(template_path), section_formats="{}")
    table_template = ResumeMdTemplate(name="Table", file_path=str(template_path), section_formats='{"skills": "table"}')

    assert "| Category | Skills |" not in render_resume_markdown_template(session, bullet_template)
    assert "| Category | Skills |" in render_resume_markdown_template(session, table_template)
