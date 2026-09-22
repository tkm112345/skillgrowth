from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from app import llm
from app.career_context import build_consult_context
from app.db import get_session
from app.models import ConsultMessage, ConsultSession, Settings

router = APIRouter(prefix="/api/consult", tags=["consult"])

TITLE_MAX_LEN = 40


class MessageIn(BaseModel):
    content: str
    locale: str = "en"


@router.get("/sessions")
def list_sessions(
    limit: int = 20, offset: int = 0, session: Session = Depends(get_session)
) -> list[ConsultSession]:
    return session.exec(
        select(ConsultSession).order_by(ConsultSession.updated_at.desc()).offset(offset).limit(limit)
    ).all()


@router.post("/sessions")
def create_session(session: Session = Depends(get_session)) -> ConsultSession:
    consult = ConsultSession()
    session.add(consult)
    session.commit()
    session.refresh(consult)
    return consult


@router.get("/sessions/{session_id}")
def get_session_detail(session_id: str, session: Session = Depends(get_session)) -> ConsultSession:
    consult = session.get(ConsultSession, session_id)
    if consult is None:
        raise HTTPException(status_code=404, detail="Consultation session not found")
    return consult


@router.delete("/sessions/{session_id}")
def delete_session(session_id: str, session: Session = Depends(get_session)):
    consult = session.get(ConsultSession, session_id)
    if consult:
        for m in session.exec(select(ConsultMessage).where(ConsultMessage.session_id == session_id)).all():
            session.delete(m)
        session.delete(consult)
        session.commit()
    return {"ok": True}


def _messages_query(session_id: str):
    return select(ConsultMessage).where(ConsultMessage.session_id == session_id).order_by(ConsultMessage.created_at)


@router.get("/sessions/{session_id}/messages")
def list_messages(session_id: str, session: Session = Depends(get_session)) -> list[ConsultMessage]:
    return session.exec(_messages_query(session_id)).all()


@router.post("/sessions/{session_id}/messages")
def send_message(
    session_id: str, payload: MessageIn, session: Session = Depends(get_session)
) -> ConsultMessage:
    consult = session.get(ConsultSession, session_id)
    if consult is None:
        raise HTTPException(status_code=404, detail="Consultation session not found")

    # Commit the user's message (and title, if this is the first one) before
    # calling the LLM, so a failed reply never loses what they typed.
    user_message = ConsultMessage(session_id=session_id, role="user", content=payload.content)
    session.add(user_message)
    if not consult.title:
        consult.title = payload.content[:TITLE_MAX_LEN]
        session.add(consult)
    session.commit()

    history = session.exec(_messages_query(session_id)).all()
    chat_messages = [{"role": m.role, "content": m.content} for m in history]
    context = build_consult_context(session)
    settings = session.get(Settings, 1)
    reply_text = llm.career_consult_reply(chat_messages, context, payload.locale, settings)

    assistant_message = ConsultMessage(session_id=session_id, role="assistant", content=reply_text)
    session.add(assistant_message)
    consult.updated_at = datetime.now(timezone.utc)
    session.add(consult)
    session.commit()
    session.refresh(assistant_message)
    return assistant_message
