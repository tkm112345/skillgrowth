import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from sqlmodel import Session, select

from app import llm, services
from app.db import UPLOAD_DIR, get_session
from app.models import EvidenceEntry, Settings, Skill

router = APIRouter(prefix="/api/evidence", tags=["evidence"])

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB, matches the portfolio upload limit


class TextEvidenceIn(BaseModel):
    source_type: str
    text: str


class EvidenceResult(BaseModel):
    evidence: EvidenceEntry
    linked_skills: list[Skill]


@router.get("")
def list_evidence(limit: int = 50, offset: int = 0, session: Session = Depends(get_session)) -> list[EvidenceEntry]:
    return session.exec(
        select(EvidenceEntry).order_by(EvidenceEntry.created_at.desc()).offset(offset).limit(limit)
    ).all()


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
    data = file.file.read()
    if len(data) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=400, detail=f"{file.filename}: file exceeds 10MB limit")

    ext = Path(file.filename or "upload.png").suffix or ".png"
    dest = UPLOAD_DIR / f"{uuid.uuid4()}{ext}"
    dest.write_bytes(data)

    entry = EvidenceEntry(source_type=source_type, raw_input=file.filename or "", file_path=str(dest))
    session.add(entry)
    session.commit()
    session.refresh(entry)

    settings = session.get(Settings, 1)
    matches = llm.extract_and_match_image(str(dest), services.existing_skills_payload(session), settings)
    linked = services.apply_matches(session, entry.id, matches)

    return EvidenceResult(evidence=entry, linked_skills=linked)
