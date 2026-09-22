from sqlmodel import Session, select

from app.models import CareerGoal, CareerVision
from app.resume_builder import build_resume_markdown
from app.routers.goals import HORIZON_LABELS, HORIZONS


def build_consult_context(session: Session) -> str:
    """Assemble everything the AI Career Consult chat should know about the
    user: the same structured data the resume draws from, plus Vision and
    career path goals — which the resume deliberately omits, but which are
    exactly what a career consultant needs to give grounded advice."""
    parts = [build_resume_markdown(session)]

    vision = session.get(CareerVision, 1)
    if vision and vision.content.strip():
        parts.append(f"## Vision\n\n{vision.content}\n")

    existing = {g.horizon: g for g in session.exec(select(CareerGoal)).all()}
    goal_lines = [
        f"- {HORIZON_LABELS[h]}: {existing[h].description}"
        for h in HORIZONS
        if h in existing and existing[h].description.strip()
    ]
    if goal_lines:
        parts.append("## Career Path Goals\n\n" + "\n".join(goal_lines) + "\n")

    return "\n".join(parts)
