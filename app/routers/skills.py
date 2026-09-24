import csv
import io
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel
from sqlmodel import Session, func, select

from app.db import get_session
from app.models import Skill, SkillLink

router = APIRouter(prefix="/api/skills", tags=["skills"])


class SkillIn(BaseModel):
    name: str
    category: str = "未分類"


class SkillResumeInclusionIn(BaseModel):
    include_in_resume: bool


class SkillMention(BaseModel):
    mention_text: str
    created_at: datetime


class SkillDetail(BaseModel):
    skill: Skill
    mentions: list[SkillMention]


class CsvImportResult(BaseModel):
    imported: list[Skill]
    skipped_rows: int


def _upsert_skill(session: Session, name: str, category: str) -> Skill | None:
    name = name.strip()
    if not name:
        return None

    existing = session.exec(select(Skill).where(func.lower(Skill.name) == name.lower())).first()
    if existing:
        existing.last_observed_at = datetime.now(timezone.utc)
        session.add(existing)
        session.commit()
        session.refresh(existing)
        return existing

    skill = Skill(name=name, category=category.strip() or "未分類")
    session.add(skill)
    session.commit()
    session.refresh(skill)
    return skill


@router.get("")
def list_skills(session: Session = Depends(get_session)):
    skills = session.exec(select(Skill).order_by(Skill.last_observed_at.desc())).all()
    counts = dict(session.exec(select(SkillLink.skill_id, func.count(SkillLink.id)).group_by(SkillLink.skill_id)).all())
    return [
        {
            "id": s.id,
            "name": s.name,
            "category": s.category,
            "first_observed_at": s.first_observed_at,
            "last_observed_at": s.last_observed_at,
            "evidence_count": counts.get(s.id, 0),
            "include_in_resume": s.include_in_resume,
        }
        for s in skills
    ]


@router.post("")
def add_skill(payload: SkillIn, session: Session = Depends(get_session)) -> Skill:
    return _upsert_skill(session, payload.name, payload.category)


@router.put("/{skill_id}")
def update_skill(skill_id: str, payload: SkillIn, session: Session = Depends(get_session)) -> Skill:
    skill = session.get(Skill, skill_id)
    if skill is None:
        raise HTTPException(status_code=404, detail="Skill not found")

    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Skill name cannot be empty")

    duplicate = session.exec(select(Skill).where(func.lower(Skill.name) == name.lower())).first()
    if duplicate and duplicate.id != skill_id:
        raise HTTPException(status_code=400, detail="Another skill with this name already exists")

    skill.name = name
    skill.category = payload.category.strip() or "未分類"
    session.add(skill)
    session.commit()
    session.refresh(skill)
    return skill


@router.put("/{skill_id}/resume-inclusion")
def set_skill_resume_inclusion(
    skill_id: str, payload: SkillResumeInclusionIn, session: Session = Depends(get_session)
) -> Skill:
    skill = session.get(Skill, skill_id)
    if skill is None:
        raise HTTPException(status_code=404, detail="Skill not found")
    skill.include_in_resume = payload.include_in_resume
    session.add(skill)
    session.commit()
    session.refresh(skill)
    return skill


@router.post("/import-csv")
def import_skills_csv(file: UploadFile = File(...), session: Session = Depends(get_session)) -> CsvImportResult:
    raw = file.file.read().decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(raw))

    imported: list[Skill] = []
    skipped_rows = 0
    for row in reader:
        name = (row.get("name") or "").strip()
        category = (row.get("category") or "").strip()
        skill = _upsert_skill(session, name, category)
        if skill:
            imported.append(skill)
        else:
            skipped_rows += 1

    return CsvImportResult(imported=imported, skipped_rows=skipped_rows)


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
    return [{"date": s.first_observed_at, "name": s.name, "category": s.category} for s in skills]


@router.get("/{skill_id}")
def skill_detail(skill_id: str, session: Session = Depends(get_session)) -> SkillDetail:
    skill = session.get(Skill, skill_id)
    links = session.exec(select(SkillLink).where(SkillLink.skill_id == skill_id)).all()
    return SkillDetail(
        skill=skill,
        mentions=[SkillMention(mention_text=link.mention_text, created_at=link.created_at) for link in links],
    )
