from sqlmodel import Session, select

from app.models import Education, Employment, LearningActivity, Project, SelfPR, Skill

SECTION_HEADERS = {
    "self_pr": "## Self PR",
    "work_history": "## Work History",
    "other_projects": "## Other Projects",
    "education": "## Education",
    "skills": "## Skills",
    "certifications": "## Certifications",
}


def _period(start, end, present_label: str = "Present") -> str:
    s = start.isoformat() if start else "?"
    e = end.isoformat() if end else present_label
    return f"{s} – {e}"


def gather_resume_context(session: Session) -> dict:
    """Collect resume data from structured records only — no LLM call.
    Shared by the Markdown builder and the Word-template renderer, so the
    two output formats never drift apart on what data they include."""
    selected_pr = session.exec(select(SelfPR).where(SelfPR.is_selected == True)).first()  # noqa: E712
    if selected_pr is None:
        # No entry explicitly selected (e.g. none ever chosen, or all
        # created before this feature existed) — fall back to the latest.
        selected_pr = session.exec(select(SelfPR).order_by(SelfPR.created_at.desc())).first()

    employment_rows = session.exec(select(Employment).order_by(Employment.start_date.desc())).all()
    projects = session.exec(select(Project)).all()
    projects_by_employment: dict[str, list[Project]] = {}
    standalone_projects: list[Project] = []
    for p in projects:
        if p.employment_id:
            projects_by_employment.setdefault(p.employment_id, []).append(p)
        else:
            standalone_projects.append(p)

    def project_dict(proj: Project) -> dict:
        return {
            "title": proj.title,
            "role": proj.role,
            "period": _period(proj.start_date, proj.end_date),
            "description": proj.description,
        }

    employment = [
        {
            "title": emp.company + (f" / {emp.department}" if emp.department else ""),
            "role": emp.role,
            "period": _period(emp.start_date, emp.end_date),
            "projects": [project_dict(p) for p in projects_by_employment.get(emp.id, [])],
        }
        for emp in employment_rows
    ]

    education_rows = session.exec(select(Education).order_by(Education.start_date.desc())).all()
    education = [
        {
            "school": edu.school,
            "header": " ".join(part for part in [edu.degree, edu.major] if part),
            "period": _period(edu.start_date, edu.end_date, present_label="?"),
            "achievements": edu.achievements,
        }
        for edu in education_rows
    ]

    skills = session.exec(
        select(Skill).where(Skill.include_in_resume == True).order_by(Skill.name)  # noqa: E712
    ).all()
    skills_by_category: dict[str, list[str]] = {}
    for s in skills:
        skills_by_category.setdefault(s.category, []).append(s.name)

    certification_rows = session.exec(
        select(LearningActivity)
        .where(LearningActivity.activity_type == "certification", LearningActivity.include_in_resume == True)  # noqa: E712
        .order_by(LearningActivity.activity_date.desc())
    ).all()
    certifications = [
        {"title": cert.title, "date": cert.activity_date.isoformat() if cert.activity_date else ""}
        for cert in certification_rows
    ]

    return {
        # None when no SelfPR row exists at all; "" is a valid (if unusual)
        # value for a row that exists but is empty — the two must stay
        # distinguishable so build_resume_markdown can match its old
        # "if selected_pr:" (object-presence) behavior exactly.
        "self_pr": selected_pr.content if selected_pr is not None else None,
        "employment": employment,
        "standalone_projects": [project_dict(p) for p in standalone_projects],
        "education": education,
        "skills_by_category": skills_by_category,
        "certifications": certifications,
    }


def build_resume_markdown(session: Session) -> str:
    """Assemble a resume as Markdown from structured records only — no LLM
    call. Sections follow a fixed order and fixed headings every time, so
    the output is deterministic and reproducible from the same data."""
    ctx = gather_resume_context(session)
    lines: list[str] = ["# Resume", ""]

    if ctx["self_pr"] is not None:
        lines += [SECTION_HEADERS["self_pr"], "", ctx["self_pr"], ""]

    if ctx["employment"]:
        lines.append(SECTION_HEADERS["work_history"])
        lines.append("")
        for emp in ctx["employment"]:
            lines.append(f"### {emp['title']}")
            lines.append(f"{emp['role']} ({emp['period']})")
            lines.append("")
            for proj in emp["projects"]:
                lines.append(f"- **{proj['title']}** — {proj['role']} ({proj['period']})")
                if proj["description"]:
                    lines.append(f"  {proj['description']}")
            lines.append("")

    if ctx["standalone_projects"]:
        lines.append(SECTION_HEADERS["other_projects"])
        lines.append("")
        for proj in ctx["standalone_projects"]:
            lines.append(f"- **{proj['title']}** — {proj['role']} ({proj['period']})")
            if proj["description"]:
                lines.append(f"  {proj['description']}")
        lines.append("")

    if ctx["education"]:
        lines.append(SECTION_HEADERS["education"])
        lines.append("")
        for edu in ctx["education"]:
            lines.append(f"### {edu['school']}")
            lines.append(f"{edu['header']} ({edu['period']})".strip())
            if edu["achievements"]:
                lines.append(edu["achievements"])
            lines.append("")

    if ctx["skills_by_category"]:
        lines.append(SECTION_HEADERS["skills"])
        lines.append("")
        for category in sorted(ctx["skills_by_category"]):
            lines.append(f"- **{category}**: {', '.join(ctx['skills_by_category'][category])}")
        lines.append("")

    if ctx["certifications"]:
        lines.append(SECTION_HEADERS["certifications"])
        lines.append("")
        for cert in ctx["certifications"]:
            date_suffix = f" ({cert['date']})" if cert["date"] else ""
            lines.append(f"- {cert['title']}{date_suffix}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"
