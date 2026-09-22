from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session

from app import llm
from app.db import get_session
from app.models import Settings

router = APIRouter(prefix="/api/settings", tags=["settings"])


class SettingsIn(BaseModel):
    openai_base_url: str
    openai_api_key: str
    llm_model: str
    llm_vision_model: str


@router.get("")
def read_settings(session: Session = Depends(get_session)) -> Settings:
    return session.get(Settings, 1)


@router.put("")
def update_settings(payload: SettingsIn, session: Session = Depends(get_session)) -> Settings:
    settings = session.get(Settings, 1)
    settings.openai_base_url = payload.openai_base_url
    settings.openai_api_key = payload.openai_api_key
    settings.llm_model = payload.llm_model
    settings.llm_vision_model = payload.llm_vision_model
    session.add(settings)
    session.commit()
    session.refresh(settings)
    return settings


@router.post("/test")
def test_settings(payload: SettingsIn) -> dict:
    candidate = Settings(
        openai_base_url=payload.openai_base_url,
        openai_api_key=payload.openai_api_key,
        llm_model=payload.llm_model,
        llm_vision_model=payload.llm_vision_model,
    )
    return llm.test_connection(candidate)
