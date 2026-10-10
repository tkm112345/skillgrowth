from datetime import datetime, timezone

from fastapi import HTTPException
from sqlmodel import Session, func, select

from app import llm
from app.models import ActivityType, EvidenceEntry, Settings, Skill, SkillLink

# Sent into the LLM prompt on every extraction/consult call, so it needs a
# cap: an unbounded list grows the prompt (latency, cost) linearly with the
# skill count over years of use. Ordered by last_observed_at so a truncation
# drops the skills least likely to recur, not an arbitrary slice.
MAX_SKILLS_IN_PROMPT = 300


def existing_skills_payload(session: Session) -> list[dict]:
    skills = session.exec(select(Skill).order_by(Skill.last_observed_at.desc()).limit(MAX_SKILLS_IN_PROMPT)).all()
    return [{"id": s.id, "name": s.name} for s in skills]


def upsert_skill(session: Session, name: str, category: str, proficiency: int | None = None) -> Skill | None:
    """Postcondition: the returned Skill's name matches `name` case-insensitively
    an existing Skill if one exists (reusing it, bumping last_observed_at —
    category/proficiency are left untouched, see comment below), otherwise a
    newly created Skill. Every caller that creates/reuses a Skill *by name* on
    behalf of a user action (manual add, CSV import, evidence extraction) must
    go through this function — it's the only thing keeping Skill.name free of
    case-insensitive duplicates. Deliberately not a DB-level constraint:
    app/backup_import.py restores Skill rows verbatim from a snapshot and is
    exempt by design (see tests/test_backup_api.py's round-trip test)."""
    name = name.strip()
    if not name:
        return None

    existing = session.exec(select(Skill).where(func.lower(Skill.name) == name.lower())).first()
    if existing:
        # Unlike name/category, proficiency is a deliberate manual judgment —
        # an automatic re-match here (CSV import, activity-extraction) must
        # never overwrite it, the same reasoning that already keeps this
        # branch from touching category.
        existing.last_observed_at = datetime.now(timezone.utc)
        session.add(existing)
        session.commit()
        session.refresh(existing)
        return existing

    skill = Skill(name=name, category=category.strip() or "未分類", proficiency=proficiency)
    session.add(skill)
    session.commit()
    session.refresh(skill)
    return skill


def apply_matches(session: Session, evidence_id: str, matches: list[dict]) -> list[Skill]:
    linked_skills: list[Skill] = []

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
            # Go through upsert_skill rather than `Skill(name=name, ...)`
            # directly: the LLM isn't guaranteed to return skill_id for an
            # existing skill, so a differently-cased name here (e.g. "python"
            # when "Python" already exists) must reuse that skill rather than
            # silently creating a case-insensitive duplicate.
            skill = upsert_skill(session, name, str(match.get("category") or "未分類"))
            if skill is None:
                continue
        else:
            # upsert_skill already bumps last_observed_at for the no-skill_id
            # branch above; this is the skill_id-matched branch's equivalent —
            # without it, a skill matched by id here (as opposed to by name)
            # never gets its "last seen" date refreshed, even though a new
            # SkillLink for it is being added right below.
            skill.last_observed_at = datetime.now(timezone.utc)
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


def find_activity_type_by_label(session: Session, label: str) -> ActivityType | None:
    """The case-insensitive lookup behind ActivityType's "label is unique
    regardless of case" invariant — shared by create/update in
    app/routers/learning.py and the activity_types loop in
    app/backup_import.py, each of which applies its own handling (reject
    vs. skip) around the same underlying check."""
    return session.exec(select(ActivityType).where(func.lower(ActivityType.label) == label.lower())).first()


def select_only(session: Session, entry) -> None:
    """Postcondition: `entry` is the only row of its table with `is_selected`
    True — every other row of the same model is flipped to False first.
    Shared by SelfPR/ResumeTemplate/RirekishoTemplate, the three "exactly
    one selected row" tables in this app (each enforces it per-table, not
    via a cross-table rule — a selected SelfPR and a selected ResumeTemplate
    coexist independently)."""
    model = type(entry)
    for other in session.exec(select(model).where(model.is_selected == True)).all():  # noqa: E712
        other.is_selected = False
        session.add(other)
    entry.is_selected = True
    session.add(entry)


def validate_section_formats(section_formats: dict[str, str], choices: dict[str, list[str]]) -> None:
    """Shared by resume_templates.py and resume_md_templates.py — both
    render the same ctx from app.resume_builder.gather_resume_context, just
    into different file formats, so the same per-section bullet/table (or
    list/table) choice applies to each. `choices` is passed in rather than
    imported here, so this stays a generic helper not coupled to either
    renderer module."""
    for key, value in section_formats.items():
        allowed = choices.get(key)
        if allowed is None or value not in allowed:
            raise HTTPException(status_code=400, detail=f"Invalid section format: {key}={value}")


def text_block(**fields: str) -> str:
    return "\n".join(f"{key}: {value}" for key, value in fields.items() if value)
