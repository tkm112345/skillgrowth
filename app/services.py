from datetime import datetime, timezone

from sqlmodel import Session, select

from app import llm
from app.models import EvidenceEntry, Settings, Skill, SkillLink


def existing_skills_payload(session: Session) -> list[dict]:
    skills = session.exec(select(Skill)).all()
    return [{"id": s.id, "name": s.name} for s in skills]


def apply_matches(session: Session, evidence_id: str, matches: list[dict]) -> list[Skill]:
    linked_skills: list[Skill] = []
    now = datetime.now(timezone.utc)

    for match in matches:
        mention_text = str(match.get("mention_text", "")).strip()
        if not mention_text:
            continue

        skill_id = match.get("skill_id")
        skill: Skill | None = session.get(Skill, skill_id) if skill_id else None

        if skill is None:
            name = str(match.get("name", "")).strip()
            if not name:
                continue
            skill = Skill(name=name, category=str(match.get("category") or "未分類"))
            session.add(skill)
            session.flush()
        else:
            skill.last_observed_at = now
            session.add(skill)

        session.add(SkillLink(evidence_id=evidence_id, skill_id=skill.id, mention_text=mention_text))
        linked_skills.append(skill)

    session.commit()
    return linked_skills


def record_evidence_and_extract(
    session: Session, source_type: str, text: str, settings: Settings
) -> tuple[EvidenceEntry, list[Skill]]:
    entry = EvidenceEntry(source_type=source_type, raw_input=text)
    session.add(entry)
    session.commit()
    session.refresh(entry)

    if not settings.skill_extraction_enabled:
        return entry, []

    matches = llm.extract_and_match_text(text, existing_skills_payload(session), settings)
    linked = apply_matches(session, entry.id, matches)
    return entry, linked


def text_block(**fields: str) -> str:
    return "\n".join(f"{key}: {value}" for key, value in fields.items() if value)
