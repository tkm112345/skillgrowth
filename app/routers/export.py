import json

from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select

from app import llm
from app.db import get_session
from app.models import EvidenceEntry, ExportSnapshot

router = APIRouter(prefix="/export", tags=["export"])


@router.post("")
def generate_export(session: Session = Depends(get_session)):
    entries = session.exec(select(EvidenceEntry)).all()
    summaries: list[str] = []
    for e in entries:
        if e.llm_extracted:
            summaries.extend(json.loads(e.llm_extracted))

    content = llm.generate_resume(summaries)
    snapshot = ExportSnapshot(content=content)
    session.add(snapshot)
    session.commit()
    return RedirectResponse("/", status_code=303)
