from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session

from app.db import get_session
from app.models import CareerVision

router = APIRouter(prefix="/api/vision", tags=["vision"])


class VisionIn(BaseModel):
    content: str


class VisionOut(BaseModel):
    content: str
    updated_at: Optional[datetime] = None


@router.get("")
def get_vision(session: Session = Depends(get_session)) -> VisionOut:
    vision = session.get(CareerVision, 1)
    if vision is None:
        return VisionOut(content="", updated_at=None)
    return VisionOut(content=vision.content, updated_at=vision.updated_at)


@router.put("")
def update_vision(payload: VisionIn, session: Session = Depends(get_session)) -> CareerVision:
    vision = session.get(CareerVision, 1)
    if vision is None:
        vision = CareerVision(id=1)
    vision.content = payload.content
    vision.updated_at = datetime.now(timezone.utc)
    session.add(vision)
    session.commit()
    session.refresh(vision)
    return vision
