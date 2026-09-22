from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session, func, select

from app.db import get_session
from app.models import Skill, SkillLink

router = APIRouter(prefix="/api/skills", tags=["skills"])


class SkillIn(BaseModel):
    name: str
    category: str = "未分類"


@router.get("")
def list_skills(session: Session = Depends(get_session)):
    skills = session.exec(select(Skill).order_by(Skill.last_observed_at.desc())).all()
    counts = dict(
        session.exec(
            select(SkillLink.skill_id, func.count(SkillLink.id)).group_by(SkillLink.skill_id)
        ).all()
    )
    return [
        {
            "id": s.id,
            "name": s.name,
            "category": s.category,
            "first_observed_at": s.first_observed_at,
            "last_observed_at": s.last_observed_at,
            "evidence_count": counts.get(s.id, 0),
        }
        for s in skills
    ]


@router.post("")
def add_skill(payload: SkillIn, session: Session = Depends(get_session)) -> Skill:
    name = payload.name.strip()
    existing = session.exec(select(Skill).where(func.lower(Skill.name) == name.lower())).first()
    if existing:
        existing.last_observed_at = datetime.now(timezone.utc)
        session.add(existing)
        session.commit()
        session.refresh(existing)
        return existing

    skill = Skill(name=name, category=payload.category.strip() or "未分類")
    session.add(skill)
    session.commit()
    session.refresh(skill)
    return skill


@router.delete("/{skill_id}")
def delete_skill(skill_id: str, session: Session = Depends(get_session)):
    skill = session.get(Skill, skill_id)
    if skill:
        for link in session.exec(select(SkillLink).where(SkillLink.skill_id == skill_id)).all():
            session.delete(link)
        session.delete(skill)
        session.commit()
    return {"ok": True}


@router.get("/timeline")
def skill_timeline(session: Session = Depends(get_session)):
    skills = session.exec(select(Skill).order_by(Skill.first_observed_at.asc())).all()
    return [
        {"date": s.first_observed_at, "name": s.name, "category": s.category}
        for s in skills
    ]


@router.get("/{skill_id}")
def skill_detail(skill_id: str, session: Session = Depends(get_session)):
    skill = session.get(Skill, skill_id)
    links = session.exec(select(SkillLink).where(SkillLink.skill_id == skill_id)).all()
    return {"skill": skill, "mentions": [{"mention_text": link.mention_text, "created_at": link.created_at} for link in links]}
