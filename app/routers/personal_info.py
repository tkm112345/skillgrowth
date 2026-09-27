import uuid
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlmodel import Session

from app.db import PERSONAL_INFO_DIR, get_session
from app.models import PersonalInfo

router = APIRouter(prefix="/api/personal-info", tags=["personal_info"])


class PersonalInfoIn(BaseModel):
    name: str = ""
    name_kana: str = ""
    birthdate: Optional[date] = None
    postal_code: str = ""
    address: str = ""
    address_kana: str = ""
    phone: str = ""
    email: str = ""


@router.get("")
def get_personal_info(session: Session = Depends(get_session)) -> PersonalInfo:
    return session.get(PersonalInfo, 1) or PersonalInfo()


@router.put("")
def update_personal_info(payload: PersonalInfoIn, session: Session = Depends(get_session)) -> PersonalInfo:
    info = session.get(PersonalInfo, 1)
    if info is None:
        info = PersonalInfo(id=1)
    for field, value in payload.model_dump().items():
        setattr(info, field, value)
    info.updated_at = datetime.now(timezone.utc)
    session.add(info)
    session.commit()
    session.refresh(info)
    return info


@router.post("/photo")
def upload_personal_info_photo(file: UploadFile = File(...), session: Session = Depends(get_session)) -> PersonalInfo:
    info = session.get(PersonalInfo, 1)
    if info is None:
        info = PersonalInfo(id=1)

    if info.photo_path:
        Path(info.photo_path).unlink(missing_ok=True)

    ext = Path(file.filename or "").suffix or ".jpg"
    dest = PERSONAL_INFO_DIR / f"{uuid.uuid4()}{ext}"
    dest.write_bytes(file.file.read())

    info.photo_path = str(dest)
    info.updated_at = datetime.now(timezone.utc)
    session.add(info)
    session.commit()
    session.refresh(info)
    return info


@router.get("/photo")
def get_personal_info_photo(session: Session = Depends(get_session)) -> FileResponse:
    info = session.get(PersonalInfo, 1)
    if info is None or not info.photo_path or not Path(info.photo_path).exists():
        raise HTTPException(status_code=404, detail="No photo uploaded")
    return FileResponse(info.photo_path)


@router.delete("/photo")
def delete_personal_info_photo(session: Session = Depends(get_session)) -> PersonalInfo:
    info = session.get(PersonalInfo, 1)
    if info is None:
        info = PersonalInfo(id=1)
    if info.photo_path:
        Path(info.photo_path).unlink(missing_ok=True)
        info.photo_path = None
        info.updated_at = datetime.now(timezone.utc)
        session.add(info)
        session.commit()
        session.refresh(info)
    return info
