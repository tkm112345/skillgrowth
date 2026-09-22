from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session, select

from app.db import get_session
from app.models import SelfPR

router = APIRouter(prefix="/api/self-pr", tags=["self_pr"])


class SelfPRIn(BaseModel):
    content: str


@router.get("")
def list_self_pr(
    limit: int = 20, offset: int = 0, session: Session = Depends(get_session)
) -> list[SelfPR]:
    return session.exec(
        select(SelfPR).order_by(SelfPR.created_at.desc()).offset(offset).limit(limit)
    ).all()


@router.post("")
def add_self_pr(payload: SelfPRIn, session: Session = Depends(get_session)) -> SelfPR:
    entry = SelfPR(content=payload.content)
    session.add(entry)
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
