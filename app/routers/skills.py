import json

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app import llm
from app.db import get_session
from app.models import EvidenceEntry

router = APIRouter(prefix="/skills", tags=["skills"])


def all_mentions(session: Session) -> list[str]:
    entries = session.exec(select(EvidenceEntry)).all()
    mentions: list[str] = []
    for e in entries:
        if e.llm_extracted:
            mentions.extend(json.loads(e.llm_extracted))
    return mentions


@router.get("/summary")
def skill_summary(session: Session = Depends(get_session)):
    return {"summary_markdown": llm.summarize_current_skills(all_mentions(session))}
