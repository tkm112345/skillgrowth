import json
from pathlib import Path

from jinja2 import Template
from sqlmodel import Session

from app.models import ResumeMdTemplate
from app.resume_builder import gather_resume_context


def _escape_cell(value: str) -> str:
    return value.replace("|", "\\|")


def _markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(_escape_cell(v) for v in row) + " |")
    return "\n".join(lines)


def _render_self_pr(text: str | None) -> str:
    return (text or "").strip()


def _render_goals(goals: list[dict]) -> str:
    return "\n".join(f"- **{goal['label']}**: {goal['description']}" for goal in goals)


def _render_activities(activities: dict) -> str:
    lines = []
    for link in activities["links"]:
        lines.append(f"- [{link['label']}]({link['url']})")
    for item in activities["portfolio"]:
        suffix = f" — {item['description']}" if item["description"] else ""
        lines.append(f"- **{item['title']}**{suffix}")
        for link in item["links"]:
            lines.append(f"  - [{link['label']}]({link['url']})")
    for talk in activities["talks"]:
        date_suffix = f" ({talk['date']})" if talk["date"] else ""
        lines.append(f"- {talk['activity_type']}: {talk['title']}{date_suffix}")
    return "\n".join(lines)


def _render_employment(employment: list[dict], fmt: str) -> str:
    if fmt == "table":
        rows = [
            [emp["title"], emp["role"], emp["period"], "; ".join(p["title"] for p in emp["projects"])]
            for emp in employment
        ]
        return _markdown_table(["Company", "Role", "Period", "Projects"], rows)
    lines = []
    for emp in employment:
        lines.append(f"**{emp['title']}**")
        lines.append(f"{emp['role']} ({emp['period']})")
        for proj in emp["projects"]:
            lines.append(f"- {proj['title']} — {proj['role']} ({proj['period']})")
            if proj["description"]:
                lines.append(f"  {proj['description']}")
        lines.append("")
    return "\n".join(lines).rstrip()


def _render_projects(projects: list[dict], fmt: str) -> str:
    if fmt == "table":
        rows = [[p["title"], p["role"], p["period"], p["description"]] for p in projects]
        return _markdown_table(["Title", "Role", "Period", "Description"], rows)
    lines = []
    for p in projects:
        lines.append(f"- {p['title']} — {p['role']} ({p['period']})")
        if p["description"]:
            lines.append(f"  {p['description']}")
    return "\n".join(lines)


def _render_education(education: list[dict]) -> str:
    lines = []
    for edu in education:
        lines.append(f"**{edu['school']}**")
        lines.append(f"{edu['header']} ({edu['period']})".strip())
        if edu["achievements"]:
            lines.append(edu["achievements"])
        lines.append("")
    return "\n".join(lines).rstrip()


def _render_skills(skills_by_category: dict[str, list[str]], fmt: str) -> str:
    categories = sorted(skills_by_category)
    if fmt == "table":
        rows = [[category, ", ".join(skills_by_category[category])] for category in categories]
        return _markdown_table(["Category", "Skills"], rows)
    return "\n".join(f"- **{category}**: {', '.join(skills_by_category[category])}" for category in categories)


def _render_certifications(certifications: list[dict], fmt: str) -> str:
    if fmt == "table":
        rows = [[c["title"], c["date"]] for c in certifications]
        return _markdown_table(["Title", "Date"], rows)
    lines = []
    for c in certifications:
        suffix = f" ({c['date']})" if c["date"] else ""
        lines.append(f"- {c['title']}{suffix}")
    return "\n".join(lines)


def render_resume_markdown_template(session: Session, template: ResumeMdTemplate) -> str:
    """Fill the uploaded Markdown template's tags with the same resume data
    `build_resume_markdown`/`render_resume_docx` use — no LLM call. Plain
    Jinja2 syntax (`{{ tag }}`), unlike the Word path's docxtpl-specific
    `{{p tag }}` paragraph tags — there's no OOXML "tag nested inside a text
    run" failure mode in plain text, so the ordinary syntax just works."""
    ctx = gather_resume_context(session)
    section_formats = json.loads(template.section_formats or "{}")

    context = {
        "self_pr": _render_self_pr(ctx["self_pr"]),
        "vision": _render_self_pr(ctx["vision"]),
        "goals": _render_goals(ctx["goals"]),
        "employment": _render_employment(ctx["employment"], section_formats.get("employment", "bullet")),
        "projects": _render_projects(ctx["standalone_projects"], section_formats.get("projects", "bullet")),
        "education": _render_education(ctx["education"]),
        "skills": _render_skills(ctx["skills_by_category"], section_formats.get("skills", "list")),
        "certifications": _render_certifications(ctx["certifications"], section_formats.get("certifications", "list")),
        "activities": _render_activities(ctx["activities"]),
        "personal_values": _render_self_pr(ctx["personal_values"]),
    }

    text = Path(template.file_path).read_text(encoding="utf-8")
    return Template(text).render(context)
