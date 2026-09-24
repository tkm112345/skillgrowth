from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from app.db import get_session
from app.models import SelfPR

router = APIRouter(prefix="/api/self-pr", tags=["self_pr"])


class SelfPRIn(BaseModel):
    content: str


def _select_only(session: Session, entry: SelfPR) -> None:
    for other in session.exec(select(SelfPR).where(SelfPR.is_selected == True)).all():  # noqa: E712
        other.is_selected = False
        session.add(other)
    entry.is_selected = True
    session.add(entry)


@router.get("")
def list_self_pr(limit: int = 20, offset: int = 0, session: Session = Depends(get_session)) -> list[SelfPR]:
    return session.exec(select(SelfPR).order_by(SelfPR.created_at.desc()).offset(offset).limit(limit)).all()


@router.post("")
def add_self_pr(payload: SelfPRIn, session: Session = Depends(get_session)) -> SelfPR:
    entry = SelfPR(content=payload.content)
    session.add(entry)
    session.flush()
    _select_only(session, entry)  # a freshly written pitch becomes the one used in the resume
    session.commit()
    session.refresh(entry)
    return entry


@router.put("/{self_pr_id}")
def update_self_pr(self_pr_id: str, payload: SelfPRIn, session: Session = Depends(get_session)) -> SelfPR:
    entry = session.get(SelfPR, self_pr_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Self PR entry not found")
    entry.content = payload.content
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return entry


@router.put("/{self_pr_id}/select")
def select_self_pr(self_pr_id: str, session: Session = Depends(get_session)) -> SelfPR:
    entry = session.get(SelfPR, self_pr_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Self PR entry not found")
    _select_only(session, entry)
    session.commit()
    session.refresh(entry)
    return entry


@router.delete("/{self_pr_id}")
def delete_self_pr(self_pr_id: str, session: Session = Depends(get_session)):
    entry = session.get(SelfPR, self_pr_id)
    if entry:
        session.delete(entry)
        session.commit()
    return {"ok": True}
