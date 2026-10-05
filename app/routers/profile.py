from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from app import services
from app.db import get_session
from app.models import Education, Employment, ExternalLink, Project, Settings, Skill

router = APIRouter(prefix="/api/profile", tags=["profile"])


class EducationResult(BaseModel):
    education: Education
    linked_skills: list[Skill]


class EmploymentResult(BaseModel):
    employment: Employment
    linked_skills: list[Skill]


class ProjectResult(BaseModel):
    project: Project
    linked_skills: list[Skill]


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


class ExternalLinkIn(BaseModel):
    label: str
    url: str


@router.get("/education", operation_id="list_education")
def list_education(session: Session = Depends(get_session)) -> list[Education]:
    return session.exec(select(Education).order_by(Education.start_date.desc())).all()


@router.post("/education", operation_id="add_education")
def create_education(payload: EducationIn, session: Session = Depends(get_session)) -> EducationResult:
    settings = session.get(Settings, 1)
    text = services.text_block(学校=payload.school, 専攻=payload.major, 学位=payload.degree, 実績=payload.achievements)
    entry, linked = services.record_evidence_and_extract(session, "education", text, settings)
    edu = Education(**payload.model_dump(), evidence_id=entry.id)
    session.add(edu)
    session.commit()
    session.refresh(edu)
    return EducationResult(education=edu, linked_skills=linked)


@router.put("/education/{education_id}", operation_id="update_education")
def update_education(education_id: str, payload: EducationIn, session: Session = Depends(get_session)) -> Education:
    edu = session.get(Education, education_id)
    if edu is None:
        raise HTTPException(status_code=404, detail="Education entry not found")
    for key, value in payload.model_dump().items():
        setattr(edu, key, value)
    session.add(edu)
    session.commit()
    session.refresh(edu)
    return edu


@router.delete("/education/{education_id}")
def delete_education(education_id: str, session: Session = Depends(get_session)):
    edu = session.get(Education, education_id)
    if edu:
        session.delete(edu)
        session.commit()
    return {"ok": True}


@router.get("/employment", operation_id="list_employment")
def list_employment(session: Session = Depends(get_session)) -> list[Employment]:
    return session.exec(select(Employment).order_by(Employment.start_date.desc())).all()


@router.post("/employment", operation_id="add_employment")
def create_employment(payload: EmploymentIn, session: Session = Depends(get_session)) -> EmploymentResult:
    settings = session.get(Settings, 1)
    text = services.text_block(会社=payload.company, 部署=payload.department, 役割=payload.role)
    entry, linked = services.record_evidence_and_extract(session, "employment", text, settings)
    emp = Employment(**payload.model_dump(), evidence_id=entry.id)
    session.add(emp)
    session.commit()
    session.refresh(emp)
    return EmploymentResult(employment=emp, linked_skills=linked)


@router.put("/employment/{employment_id}", operation_id="update_employment")
def update_employment(employment_id: str, payload: EmploymentIn, session: Session = Depends(get_session)) -> Employment:
    emp = session.get(Employment, employment_id)
    if emp is None:
        raise HTTPException(status_code=404, detail="Employment entry not found")
    for key, value in payload.model_dump().items():
        setattr(emp, key, value)
    session.add(emp)
    session.commit()
    session.refresh(emp)
    return emp


@router.delete("/employment/{employment_id}")
def delete_employment(employment_id: str, session: Session = Depends(get_session)):
    emp = session.get(Employment, employment_id)
    if emp:
        session.delete(emp)
        session.commit()
    return {"ok": True}


@router.get("/projects", operation_id="list_projects")
def list_projects(session: Session = Depends(get_session)) -> list[Project]:
    return session.exec(select(Project).order_by(Project.start_date.desc())).all()


@router.post("/projects", operation_id="add_project")
def create_project(payload: ProjectIn, session: Session = Depends(get_session)) -> ProjectResult:
    settings = session.get(Settings, 1)
    text = services.text_block(プロジェクト=payload.title, 役割=payload.role, 内容=payload.description)
    entry, linked = services.record_evidence_and_extract(session, "project", text, settings)
    project = Project(**payload.model_dump(), evidence_id=entry.id)
    session.add(project)
    session.commit()
    session.refresh(project)
    return ProjectResult(project=project, linked_skills=linked)


@router.put("/projects/{project_id}", operation_id="update_project")
def update_project(project_id: str, payload: ProjectIn, session: Session = Depends(get_session)) -> Project:
    project = session.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    for key, value in payload.model_dump().items():
        setattr(project, key, value)
    session.add(project)
    session.commit()
    session.refresh(project)
    return project


@router.delete("/projects/{project_id}")
def delete_project(project_id: str, session: Session = Depends(get_session)):
    project = session.get(Project, project_id)
    if project:
        session.delete(project)
        session.commit()
    return {"ok": True}


@router.get("/links", operation_id="list_profile_links")
def list_links(session: Session = Depends(get_session)) -> list[ExternalLink]:
    return session.exec(select(ExternalLink).order_by(ExternalLink.created_at.asc())).all()


@router.post("/links", operation_id="add_profile_link")
def create_link(payload: ExternalLinkIn, session: Session = Depends(get_session)) -> ExternalLink:
    link = ExternalLink(label=payload.label.strip(), url=payload.url.strip())
    session.add(link)
    session.commit()
    session.refresh(link)
    return link


@router.delete("/links/{link_id}")
def delete_link(link_id: str, session: Session = Depends(get_session)):
    link = session.get(ExternalLink, link_id)
    if link:
        session.delete(link)
        session.commit()
    return {"ok": True}
