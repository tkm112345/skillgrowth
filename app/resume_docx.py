import json
from io import BytesIO

from docxtpl import DocxTemplate
from sqlmodel import Session

from app.models import ResumeTemplate
from app.resume_builder import gather_resume_context

# Sections whose layout the app UI lets the user pick, independent of the
# uploaded template's own content — the template just places the tag,
# the format choice decides whether it's rendered as a bullet list or a
# native Word table.
SECTION_FORMAT_CHOICES: dict[str, list[str]] = {
    "employment": ["bullet", "table"],
    "projects": ["bullet", "table"],
    "skills": ["list", "table"],
    "certifications": ["list", "table"],
}


def _add_table(subdoc, headers: list[str], rows: list[list[str]]) -> None:
    table = subdoc.add_table(rows=1, cols=len(headers))
    try:
        table.style = "Table Grid"
    except KeyError:
        # The uploaded template doesn't define this built-in style — an
        # unstyled (borderless) table still renders correctly.
        pass
    for cell, header in zip(table.rows[0].cells, headers):
        cell.text = header
    for row_values in rows:
        cells = table.add_row().cells
        for cell, value in zip(cells, row_values):
            cell.text = value


def _build_self_pr_subdoc(tpl: DocxTemplate, text: str | None):
    subdoc = tpl.new_subdoc()
    for line in (text or "").split("\n"):
        if line.strip():
            subdoc.add_paragraph(line)
    return subdoc


def _build_employment_subdoc(tpl: DocxTemplate, employment: list[dict], fmt: str):
    subdoc = tpl.new_subdoc()
    if fmt == "table":
        rows = [
            [emp["title"], emp["role"], emp["period"], "; ".join(p["title"] for p in emp["projects"])]
            for emp in employment
        ]
        _add_table(subdoc, ["Company", "Role", "Period", "Projects"], rows)
        return subdoc
    for emp in employment:
        p = subdoc.add_paragraph()
        p.add_run(emp["title"]).bold = True
        subdoc.add_paragraph(f"{emp['role']} ({emp['period']})")
        for proj in emp["projects"]:
            subdoc.add_paragraph(f"• {proj['title']} — {proj['role']} ({proj['period']})")
            if proj["description"]:
                subdoc.add_paragraph(proj["description"])
    return subdoc


def _build_projects_subdoc(tpl: DocxTemplate, projects: list[dict], fmt: str):
    subdoc = tpl.new_subdoc()
    if fmt == "table":
        rows = [[p["title"], p["role"], p["period"], p["description"]] for p in projects]
        _add_table(subdoc, ["Title", "Role", "Period", "Description"], rows)
        return subdoc
    for p in projects:
        subdoc.add_paragraph(f"• {p['title']} — {p['role']} ({p['period']})")
        if p["description"]:
            subdoc.add_paragraph(p["description"])
    return subdoc


def _build_education_subdoc(tpl: DocxTemplate, education: list[dict]):
    subdoc = tpl.new_subdoc()
    for edu in education:
        p = subdoc.add_paragraph()
        p.add_run(edu["school"]).bold = True
        subdoc.add_paragraph(f"{edu['header']} ({edu['period']})".strip())
        if edu["achievements"]:
            subdoc.add_paragraph(edu["achievements"])
    return subdoc


def _build_skills_subdoc(tpl: DocxTemplate, skills_by_category: dict[str, list[str]], fmt: str):
    subdoc = tpl.new_subdoc()
    categories = sorted(skills_by_category)
    if fmt == "table":
        rows = [[category, ", ".join(skills_by_category[category])] for category in categories]
        _add_table(subdoc, ["Category", "Skills"], rows)
        return subdoc
    for category in categories:
        subdoc.add_paragraph(f"• {category}: {', '.join(skills_by_category[category])}")
    return subdoc


def _build_certifications_subdoc(tpl: DocxTemplate, certifications: list[dict], fmt: str):
    subdoc = tpl.new_subdoc()
    if fmt == "table":
        rows = [[c["title"], c["date"]] for c in certifications]
        _add_table(subdoc, ["Title", "Date"], rows)
        return subdoc
    for c in certifications:
        suffix = f" ({c['date']})" if c["date"] else ""
        subdoc.add_paragraph(f"• {c['title']}{suffix}")
    return subdoc


def render_resume_docx(session: Session, template: ResumeTemplate) -> bytes:
    """Fill the uploaded .docx template's tags with the same resume data
    `build_resume_markdown` uses — no LLM call. Section tags whose format is
    configurable (see SECTION_FORMAT_CHOICES) are rendered as a bullet list
    or a native Word table per `template.section_formats`, defaulting to
    the first choice for any section not set."""
    ctx = gather_resume_context(session)
    section_formats = json.loads(template.section_formats or "{}")

    tpl = DocxTemplate(template.file_path)
    context = {
        "self_pr": _build_self_pr_subdoc(tpl, ctx["self_pr"]),
        "employment": _build_employment_subdoc(tpl, ctx["employment"], section_formats.get("employment", "bullet")),
        "projects": _build_projects_subdoc(tpl, ctx["standalone_projects"], section_formats.get("projects", "bullet")),
        "education": _build_education_subdoc(tpl, ctx["education"]),
        "skills": _build_skills_subdoc(tpl, ctx["skills_by_category"], section_formats.get("skills", "list")),
        "certifications": _build_certifications_subdoc(
            tpl, ctx["certifications"], section_formats.get("certifications", "list")
        ),
    }
    tpl.render(context)

    buf = BytesIO()
    tpl.save(buf)
    return buf.getvalue()
