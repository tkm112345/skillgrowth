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


def build_resume_markdown(session: Session) -> str:
    """Assemble a resume as Markdown from structured records only — no LLM
    call. Sections follow a fixed order and fixed headings every time, so
    the output is deterministic and reproducible from the same data."""
    lines: list[str] = ["# Resume", ""]

    selected_pr = session.exec(select(SelfPR).where(SelfPR.is_selected == True)).first()  # noqa: E712
    if selected_pr is None:
        # No entry explicitly selected (e.g. none ever chosen, or all
        # created before this feature existed) — fall back to the latest.
        selected_pr = session.exec(select(SelfPR).order_by(SelfPR.created_at.desc())).first()
    if selected_pr:
        lines += [SECTION_HEADERS["self_pr"], "", selected_pr.content, ""]

    employment = session.exec(select(Employment).order_by(Employment.start_date.desc())).all()
    projects = session.exec(select(Project)).all()
    projects_by_employment: dict[str, list[Project]] = {}
    standalone_projects: list[Project] = []
    for p in projects:
        if p.employment_id:
            projects_by_employment.setdefault(p.employment_id, []).append(p)
        else:
            standalone_projects.append(p)

    if employment:
        lines.append(SECTION_HEADERS["work_history"])
        lines.append("")
        for emp in employment:
            title = emp.company + (f" / {emp.department}" if emp.department else "")
            lines.append(f"### {title}")
            lines.append(f"{emp.role} ({_period(emp.start_date, emp.end_date)})")
            lines.append("")
            for proj in projects_by_employment.get(emp.id, []):
                lines.append(f"- **{proj.title}** — {proj.role} ({_period(proj.start_date, proj.end_date)})")
                if proj.description:
                    lines.append(f"  {proj.description}")
            lines.append("")

    if standalone_projects:
        lines.append(SECTION_HEADERS["other_projects"])
        lines.append("")
        for proj in standalone_projects:
            lines.append(f"- **{proj.title}** — {proj.role} ({_period(proj.start_date, proj.end_date)})")
            if proj.description:
                lines.append(f"  {proj.description}")
        lines.append("")

    education = session.exec(select(Education).order_by(Education.start_date.desc())).all()
    if education:
        lines.append(SECTION_HEADERS["education"])
        lines.append("")
        for edu in education:
            lines.append(f"### {edu.school}")
            header = " ".join(part for part in [edu.degree, edu.major] if part)
            lines.append(f"{header} ({_period(edu.start_date, edu.end_date, present_label='?')})".strip())
            if edu.achievements:
                lines.append(edu.achievements)
            lines.append("")

    skills = session.exec(
        select(Skill).where(Skill.include_in_resume == True).order_by(Skill.name)  # noqa: E712
    ).all()
    if skills:
        lines.append(SECTION_HEADERS["skills"])
        lines.append("")
        by_category: dict[str, list[str]] = {}
        for s in skills:
            by_category.setdefault(s.category, []).append(s.name)
        for category in sorted(by_category):
            lines.append(f"- **{category}**: {', '.join(by_category[category])}")
        lines.append("")

    certifications = session.exec(
        select(LearningActivity)
        .where(LearningActivity.activity_type == "certification")
        .order_by(LearningActivity.activity_date.desc())
    ).all()
    if certifications:
        lines.append(SECTION_HEADERS["certifications"])
        lines.append("")
        for cert in certifications:
            date_suffix = f" ({cert.activity_date.isoformat()})" if cert.activity_date else ""
            lines.append(f"- {cert.title}{date_suffix}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"
