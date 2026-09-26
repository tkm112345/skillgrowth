from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session, text

from app.db import get_session

router = APIRouter(prefix="/api/search", tags=["search"])


class SearchResult(BaseModel):
    entity_type: str
    entity_id: str
    title: str
    snippet: str


@router.get("")
def search(q: str = "", session: Session = Depends(get_session)) -> list[SearchResult]:
    q = q.strip()
    if len(q) < 2:
        return []
    # Quote each token and mark it prefix-matching, so FTS5 operator syntax
    # in raw user input (-, ", *, NEAR, ...) can't be misinterpreted.
    match_query = " ".join('"' + token.replace('"', '""') + '"*' for token in q.split())
    try:
        rows = session.exec(
            text(
                "SELECT entity_type, entity_id, title, "
                "snippet(search_index, 3, '[', ']', '…', 12) "
                "FROM search_index WHERE search_index MATCH :q ORDER BY rank LIMIT 30"
            ),
            params={"q": match_query},
        ).all()
    except Exception:
        # Malformed FTS5 query syntax that slipped through the quoting
        # above (e.g. an empty token) — degrade to no results rather than
        # a 500.
        return []
    return [SearchResult(entity_type=r[0], entity_id=r[1], title=r[2], snippet=r[3]) for r in rows]
