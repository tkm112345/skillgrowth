from app import services
from app.models import EvidenceEntry, Skill


def test_apply_matches_creates_new_skill(session):
    entry = EvidenceEntry(source_type="checkin", raw_input="learned Python")
    session.add(entry)
    session.commit()
    session.refresh(entry)

    linked = services.apply_matches(
        session,
        entry.id,
        [{"mention_text": "Python", "skill_id": None, "name": "Python", "category": "技術"}],
    )

    assert len(linked) == 1
    assert linked[0].name == "Python"
    assert linked[0].category == "技術"


def test_apply_matches_reuses_existing_skill(session):
    existing = Skill(name="Python", category="技術")
    session.add(existing)
    session.commit()
    session.refresh(existing)
    first_seen = existing.first_observed_at

    entry = EvidenceEntry(source_type="checkin", raw_input="more Python work")
    session.add(entry)
    session.commit()
    session.refresh(entry)

    linked = services.apply_matches(
        session,
        entry.id,
        [{"mention_text": "Python again", "skill_id": existing.id, "name": None, "category": None}],
    )

    all_skills = services.existing_skills_payload(session)
    assert len(all_skills) == 1  # no duplicate created
    assert linked[0].id == existing.id
    assert linked[0].first_observed_at == first_seen


def test_apply_matches_skips_empty_mention(session):
    entry = EvidenceEntry(source_type="checkin", raw_input="")
    session.add(entry)
    session.commit()
    session.refresh(entry)

    linked = services.apply_matches(session, entry.id, [{"mention_text": "  ", "skill_id": None}])

    assert linked == []
    assert services.existing_skills_payload(session) == []


def test_text_block_drops_empty_fields():
    result = services.text_block(会社="Acme", 部署="", 役割="Engineer")
    assert result == "会社: Acme\n役割: Engineer"
