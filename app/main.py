import json
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

load_dotenv()

from app.db import get_session, init_db  # noqa: E402
from app.models import EvidenceEntry, ExportSnapshot  # noqa: E402
from app.routers import evidence, export, skills  # noqa: E402

app = FastAPI(title="skillgrowth")
app.include_router(evidence.router)
app.include_router(skills.router)
app.include_router(export.router)

BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/", response_class=HTMLResponse)
def index(request: Request, session: Session = Depends(get_session)):
    entries = session.exec(
        select(EvidenceEntry).order_by(EvidenceEntry.created_at.desc())
    ).all()
    latest_export = session.exec(
        select(ExportSnapshot).order_by(ExportSnapshot.generated_at.desc())
    ).first()

    entry_rows = [
        {
            "id": e.id,
            "source_type": e.source_type,
            "raw_input": e.raw_input,
            "created_at": e.created_at,
            "mentions": json.loads(e.llm_extracted) if e.llm_extracted else [],
        }
        for e in entries
    ]

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "entries": entry_rows,
            "latest_export": latest_export,
        },
    )
