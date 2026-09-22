from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session, select

from app import services
from app.db import get_session
from app.models import Education, Employment, Project, Settings

router = APIRouter(prefix="/api/profile", tags=["profile"])


class EducationIn(BaseModel):
    school: str
    degree: str = ""
    major: str = ""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    achievements: str = ""


class EmploymentIn(BaseModel):
    company: str
    department: str = ""
    role: str = ""
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class ProjectIn(BaseModel):
    employment_id: Optional[str] = None
    title: str
    role: str = ""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: str = ""


@router.get("/education")
def list_education(session: Session = Depends(get_session)) -> list[Education]:
    return session.exec(select(Education).order_by(Education.start_date.desc())).all()


@router.post("/education")
def create_education(payload: EducationIn, session: Session = Depends(get_session)):
    settings = session.get(Settings, 1)
    text = services.text_block(
        学校=payload.school, 専攻=payload.major, 学位=payload.degree, 実績=payload.achievements
    )
    entry, linked = services.record_evidence_and_extract(session, "education", text, settings)
    edu = Education(**payload.model_dump(), evidence_id=entry.id)
    session.add(edu)
    session.commit()
    session.refresh(edu)
    return {"education": edu, "linked_skills": linked}


@router.delete("/education/{education_id}")
def delete_education(education_id: str, session: Session = Depends(get_session)):
    edu = session.get(Education, education_id)
    if edu:
        session.delete(edu)
        session.commit()
    return {"ok": True}


@router.get("/employment")
def list_employment(session: Session = Depends(get_session)) -> list[Employment]:
    return session.exec(select(Employment).order_by(Employment.start_date.desc())).all()


@router.post("/employment")
def create_employment(payload: EmploymentIn, session: Session = Depends(get_session)):
    settings = session.get(Settings, 1)
    text = services.text_block(会社=payload.company, 部署=payload.department, 役割=payload.role)
    entry, linked = services.record_evidence_and_extract(session, "employment", text, settings)
    emp = Employment(**payload.model_dump(), evidence_id=entry.id)
    session.add(emp)
    session.commit()
    session.refresh(emp)
    return {"employment": emp, "linked_skills": linked}


@router.delete("/employment/{employment_id}")
def delete_employment(employment_id: str, session: Session = Depends(get_session)):
    emp = session.get(Employment, employment_id)
    if emp:
        session.delete(emp)
        session.commit()
    return {"ok": True}


@router.get("/projects")
def list_projects(session: Session = Depends(get_session)) -> list[Project]:
    return session.exec(select(Project).order_by(Project.start_date.desc())).all()


@router.post("/projects")
def create_project(payload: ProjectIn, session: Session = Depends(get_session)):
    settings = session.get(Settings, 1)
    text = services.text_block(
        プロジェクト=payload.title, 役割=payload.role, 内容=payload.description
    )
    entry, linked = services.record_evidence_and_extract(session, "project", text, settings)
    project = Project(**payload.model_dump(), evidence_id=entry.id)
    session.add(project)
    session.commit()
    session.refresh(project)
    return {"project": project, "linked_skills": linked}


@router.delete("/projects/{project_id}")
def delete_project(project_id: str, session: Session = Depends(get_session)):
    project = session.get(Project, project_id)
    if project:
        session.delete(project)
        session.commit()
    return {"ok": True}
