import json
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import RedirectResponse
from sqlmodel import Session

from app import llm
from app.db import UPLOAD_DIR, get_session
from app.models import EvidenceEntry

router = APIRouter(prefix="/evidence", tags=["evidence"])


@router.post("/text")
def add_text_evidence(
    source_type: str = Form(...),
    text: str = Form(...),
    session: Session = Depends(get_session),
):
    mentions = llm.extract_skills_from_text(text)
    entry = EvidenceEntry(
        source_type=source_type,
        raw_input=text,
        llm_extracted=json.dumps(mentions, ensure_ascii=False),
    )
    session.add(entry)
    session.commit()
    return RedirectResponse("/", status_code=303)


@router.post("/image")
def add_image_evidence(
    source_type: str = Form("certification"),
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
):
    ext = Path(file.filename or "upload.png").suffix or ".png"
    dest = UPLOAD_DIR / f"{uuid.uuid4()}{ext}"
    dest.write_bytes(file.file.read())

    mentions = llm.extract_skills_from_image(str(dest))
    entry = EvidenceEntry(
        source_type=source_type,
        raw_input=file.filename or "",
        file_path=str(dest),
        llm_extracted=json.dumps(mentions, ensure_ascii=False),
    )
    session.add(entry)
    session.commit()
    return RedirectResponse("/", status_code=303)
