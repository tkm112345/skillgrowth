from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session

from app.db import get_session
from app.models import CareerVision

router = APIRouter(prefix="/api/vision", tags=["vision"])


class VisionIn(BaseModel):
    content: str


@router.get("")
def get_vision(session: Session = Depends(get_session)) -> CareerVision:
    return session.get(CareerVision, 1) or CareerVision(id=1)


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
