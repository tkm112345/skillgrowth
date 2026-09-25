from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session

from app import llm
from app.db import get_session
from app.models import Settings

router = APIRouter(prefix="/api/settings", tags=["settings"])

# GET never returns the real key (it would otherwise be readable by anything
# that can call this API, e.g. a browser extension or devtools). PUT and
# /test treat this exact placeholder as "unchanged" so the frontend can round
# trip the field without the user retyping the key on every save.
MASKED_KEY_PLACEHOLDER = "••••••••"


class SettingsIn(BaseModel):
    openai_base_url: str
    openai_api_key: str
    llm_model: str
    llm_vision_model: str
    skill_extraction_enabled: bool = False


def _mask(key: str) -> str:
    return MASKED_KEY_PLACEHOLDER if key else ""


@router.get("")
def read_settings(session: Session = Depends(get_session)) -> Settings:
    settings = session.get(Settings, 1)
    settings.openai_api_key = _mask(settings.openai_api_key)
    return settings


@router.put("")
def update_settings(payload: SettingsIn, session: Session = Depends(get_session)) -> Settings:
    settings = session.get(Settings, 1)
    settings.openai_base_url = payload.openai_base_url
    if payload.openai_api_key != MASKED_KEY_PLACEHOLDER:
        settings.openai_api_key = payload.openai_api_key
    settings.llm_model = payload.llm_model
    settings.llm_vision_model = payload.llm_vision_model
    settings.skill_extraction_enabled = payload.skill_extraction_enabled
    session.add(settings)
    session.commit()
    session.refresh(settings)
    settings.openai_api_key = _mask(settings.openai_api_key)
    return settings


@router.post("/test")
def test_settings(payload: SettingsIn, session: Session = Depends(get_session)) -> dict:
    api_key = payload.openai_api_key
    if api_key == MASKED_KEY_PLACEHOLDER:
        api_key = session.get(Settings, 1).openai_api_key
    candidate = Settings(
        openai_base_url=payload.openai_base_url,
        openai_api_key=api_key,
        llm_model=payload.llm_model,
        llm_vision_model=payload.llm_vision_model,
    )
    return llm.test_connection(candidate)
