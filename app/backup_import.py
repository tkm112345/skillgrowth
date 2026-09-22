from datetime import date, datetime

from sqlmodel import Session

from app.models import (
    CareerGoal,
    CareerGoalHistory,
    CareerVision,
    ConsultMessage,
    ConsultSession,
    Education,
    Employment,
    EvidenceEntry,
    ExportSnapshot,
    ExternalLink,
    LearningActivity,
    Project,
    SelfPR,
    Skill,
    SkillLink,
)


def _dt(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value) if value else None


def _d(value: str | None) -> date | None:
    return date.fromisoformat(value) if value else None


def import_backup(session: Session, data: dict, track: dict[str, list[str]] | None = None) -> dict:
    """Restore (or seed) records from a backup-shaped dict.

    Every record gets a freshly generated id, and foreign keys (evidence_id,
    skill_id, employment_id) are remapped from the old ids in `data` to the
    new ones, since re-running an import must never collide with existing
    rows. CareerGoal is keyed by horizon (not id) and CareerVision is a
    singleton (id=1); both only fill in a value that's still empty, so
    importing never silently overwrites a goal or vision the user has
    already written.

    If `track` is given, the real id of every row this call creates (or, for
    CareerGoal, the horizon it filled in, or "1" for CareerVision) is
    appended under a table-name key — used by the sample-data loader so a
    later reset can remove exactly what it added, and nothing else.
    """

    def note(table: str, record_id: str) -> None:
        if track is not None:
            track.setdefault(table, []).append(record_id)

    counts: dict[str, int] = {}

    evidence_id_map: dict[str, str] = {}
    for row in data.get("evidence", []):
        entry = EvidenceEntry(
            source_type=row["source_type"],
            raw_input=row["raw_input"],
            file_path=row.get("file_path"),
            created_at=_dt(row["created_at"]),
        )
        session.add(entry)
        session.flush()
        evidence_id_map[row["id"]] = entry.id
        note("evidence", entry.id)
    counts["evidence"] = len(evidence_id_map)

    skill_id_map: dict[str, str] = {}
    for row in data.get("skills", []):
        skill = Skill(
            name=row["name"],
            category=row["category"],
            first_observed_at=_dt(row["first_observed_at"]),
            last_observed_at=_dt(row["last_observed_at"]),
            include_in_resume=row.get("include_in_resume", True),
        )
        session.add(skill)
        session.flush()
        skill_id_map[row["id"]] = skill.id
        note("skill", skill.id)
    counts["skills"] = len(skill_id_map)

    counts["skill_links"] = 0
    for row in data.get("skill_links", []):
        ev_id = evidence_id_map.get(row["evidence_id"])
        sk_id = skill_id_map.get(row["skill_id"])
        if not ev_id or not sk_id:
            continue
        link = SkillLink(
            evidence_id=ev_id,
            skill_id=sk_id,
            mention_text=row["mention_text"],
            created_at=_dt(row["created_at"]),
        )
        session.add(link)
        session.flush()
        note("skill_link", link.id)
        counts["skill_links"] += 1

    employment_id_map: dict[str, str] = {}
    for row in data.get("employment", []):
        emp = Employment(
            company=row["company"],
            department=row.get("department", ""),
            role=row.get("role", ""),
            start_date=_d(row.get("start_date")),
            end_date=_d(row.get("end_date")),
            evidence_id=evidence_id_map.get(row.get("evidence_id")),
        )
        session.add(emp)
        session.flush()
        employment_id_map[row["id"]] = emp.id
        note("employment", emp.id)
    counts["employment"] = len(employment_id_map)

    counts["education"] = 0
    for row in data.get("education", []):
        edu = Education(
            school=row["school"],
            degree=row.get("degree", ""),
            major=row.get("major", ""),
            start_date=_d(row.get("start_date")),
            end_date=_d(row.get("end_date")),
            achievements=row.get("achievements", ""),
            evidence_id=evidence_id_map.get(row.get("evidence_id")),
        )
        session.add(edu)
        session.flush()
        note("education", edu.id)
        counts["education"] += 1

    counts["projects"] = 0
    for row in data.get("projects", []):
        project = Project(
            employment_id=employment_id_map.get(row.get("employment_id")),
            title=row["title"],
            role=row.get("role", ""),
            start_date=_d(row.get("start_date")),
            end_date=_d(row.get("end_date")),
            description=row.get("description", ""),
            evidence_id=evidence_id_map.get(row.get("evidence_id")),
        )
        session.add(project)
        session.flush()
        note("project", project.id)
        counts["projects"] += 1

    counts["learning_activities"] = 0
    for row in data.get("learning_activities", []):
        activity = LearningActivity(
            activity_type=row["activity_type"],
            title=row["title"],
            activity_date=_d(row.get("activity_date")),
            notes=row.get("notes", ""),
            evidence_id=evidence_id_map.get(row.get("evidence_id")),
        )
        session.add(activity)
        session.flush()
        note("learning_activity", activity.id)
        counts["learning_activities"] += 1

    counts["external_links"] = 0
    for row in data.get("external_links", []):
        link = ExternalLink(label=row["label"], url=row["url"], created_at=_dt(row.get("created_at")))
        session.add(link)
        session.flush()
        note("external_link", link.id)
        counts["external_links"] += 1

    counts["career_goals"] = 0
    for row in data.get("career_goals", []):
        existing = session.get(CareerGoal, row["horizon"])
        if existing is None:
            session.add(CareerGoal(horizon=row["horizon"], description=row.get("description", "")))
            note("career_goal", row["horizon"])
            counts["career_goals"] += 1
        elif not existing.description.strip():
            existing.description = row.get("description", "")
            session.add(existing)
            note("career_goal", row["horizon"])
            counts["career_goals"] += 1

    counts["career_goal_history"] = 0
    for row in data.get("career_goal_history", []):
        entry = CareerGoalHistory(
            horizon=row["horizon"], description=row["description"], created_at=_dt(row.get("created_at"))
        )
        session.add(entry)
        session.flush()
        note("career_goal_history", entry.id)
        counts["career_goal_history"] += 1

    counts["career_vision"] = 0
    for row in data.get("career_vision", []):
        existing = session.get(CareerVision, 1)
        if existing is None:
            session.add(CareerVision(id=1, content=row.get("content", ""), updated_at=_dt(row.get("updated_at"))))
            note("career_vision", "1")
            counts["career_vision"] += 1
        elif not existing.content.strip():
            existing.content = row.get("content", "")
            existing.updated_at = _dt(row.get("updated_at")) or existing.updated_at
            session.add(existing)
            note("career_vision", "1")
            counts["career_vision"] += 1

    counts["resume_exports"] = 0
    for row in data.get("resume_exports", []):
        snapshot = ExportSnapshot(
            content=row["content"],
            generated_at=_dt(row.get("generated_at")),
            edited_at=_dt(row.get("edited_at")),
        )
        session.add(snapshot)
        session.flush()
        note("resume_export", snapshot.id)
        counts["resume_exports"] += 1

    counts["self_prs"] = 0
    for row in data.get("self_prs", []):
        # is_selected is deliberately never imported — importing adds
        # historical records, it must never silently change which entry
        # the resume currently uses, or violate the "at most one selected
        # row" invariant that app/routers/self_pr.py::_select_only keeps.
        entry = SelfPR(content=row["content"], created_at=_dt(row.get("created_at")))
        session.add(entry)
        session.flush()
        note("self_pr", entry.id)
        counts["self_prs"] += 1

    consult_session_id_map: dict[str, str] = {}
    for row in data.get("consult_sessions", []):
        consult_session = ConsultSession(
            title=row.get("title", ""),
            created_at=_dt(row.get("created_at")),
            updated_at=_dt(row.get("updated_at")),
        )
        session.add(consult_session)
        session.flush()
        consult_session_id_map[row["id"]] = consult_session.id
        note("consult_session", consult_session.id)
    counts["consult_sessions"] = len(consult_session_id_map)

    counts["consult_messages"] = 0
    for row in data.get("consult_messages", []):
        session_id = consult_session_id_map.get(row["session_id"])
        if not session_id:
            continue
        message = ConsultMessage(
            session_id=session_id,
            role=row["role"],
            content=row["content"],
            created_at=_dt(row.get("created_at")),
        )
        session.add(message)
        session.flush()
        note("consult_message", message.id)
        counts["consult_messages"] += 1

    session.commit()
    return counts
