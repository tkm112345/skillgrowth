import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, UploadFile
from pydantic import BaseModel
from sqlmodel import Session, select

from app import llm, services
from app.db import UPLOAD_DIR, get_session
from app.models import EvidenceEntry, Settings, Skill

router = APIRouter(prefix="/api/evidence", tags=["evidence"])


class TextEvidenceIn(BaseModel):
    source_type: str
    text: str


class EvidenceResult(BaseModel):
    evidence: EvidenceEntry
    linked_skills: list[Skill]


@router.get("")
def list_evidence(session: Session = Depends(get_session)) -> list[EvidenceEntry]:
    return session.exec(select(EvidenceEntry).order_by(EvidenceEntry.created_at.desc())).all()


@router.post("/text")
def add_text_evidence(payload: TextEvidenceIn, session: Session = Depends(get_session)) -> EvidenceResult:
    settings = session.get(Settings, 1)
    entry, linked = services.record_evidence_and_extract(session, payload.source_type, payload.text, settings)
    return EvidenceResult(evidence=entry, linked_skills=linked)


@router.post("/image")
def add_image_evidence(
    source_type: str = Form("certification"),
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
) -> EvidenceResult:
    ext = Path(file.filename or "upload.png").suffix or ".png"
    dest = UPLOAD_DIR / f"{uuid.uuid4()}{ext}"
    dest.write_bytes(file.file.read())

    entry = EvidenceEntry(source_type=source_type, raw_input=file.filename or "", file_path=str(dest))
    session.add(entry)
    session.commit()
    session.refresh(entry)

    settings = session.get(Settings, 1)
    matches = llm.extract_and_match_image(str(dest), services.existing_skills_payload(session), settings)
    linked = services.apply_matches(session, entry.id, matches)

    return EvidenceResult(evidence=entry, linked_skills=linked)
