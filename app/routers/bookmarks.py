from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from app.db import get_session
from app.models import Bookmark

router = APIRouter(prefix="/api/bookmarks", tags=["bookmarks"])


class BookmarkIn(BaseModel):
    url: str
    title: str
    memo: str = ""


@router.get("")
def list_bookmarks(session: Session = Depends(get_session)) -> list[Bookmark]:
    return session.exec(select(Bookmark).order_by(Bookmark.created_at.desc())).all()


@router.post("")
def create_bookmark(payload: BookmarkIn, session: Session = Depends(get_session)) -> Bookmark:
    url = payload.url.strip()
    title = payload.title.strip()
    if not url or not title:
        raise HTTPException(status_code=400, detail="URL and title cannot be empty")
    bookmark = Bookmark(url=url, title=title, memo=payload.memo)
    session.add(bookmark)
    session.commit()
    session.refresh(bookmark)
    return bookmark


@router.put("/{bookmark_id}")
def update_bookmark(bookmark_id: str, payload: BookmarkIn, session: Session = Depends(get_session)) -> Bookmark:
    bookmark = session.get(Bookmark, bookmark_id)
    if bookmark is None:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    url = payload.url.strip()
    title = payload.title.strip()
    if not url or not title:
        raise HTTPException(status_code=400, detail="URL and title cannot be empty")
    bookmark.url = url
    bookmark.title = title
    bookmark.memo = payload.memo
    session.add(bookmark)
    session.commit()
    session.refresh(bookmark)
    return bookmark


@router.delete("/{bookmark_id}")
def delete_bookmark(bookmark_id: str, session: Session = Depends(get_session)):
    bookmark = session.get(Bookmark, bookmark_id)
    if bookmark:
        session.delete(bookmark)
        session.commit()
    return {"ok": True}
