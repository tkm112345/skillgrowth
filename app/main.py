from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

load_dotenv()

from app.db import init_db  # noqa: E402
from app.routers import backup, evidence, export, goals, learning, profile, settings, skills  # noqa: E402

VERSION = (Path(__file__).resolve().parent.parent / "VERSION").read_text().strip()

app = FastAPI(title="skillgrowth", version=VERSION)


@app.get("/api/version")
def get_version() -> dict:
    return {"version": VERSION}


app.include_router(evidence.router)
app.include_router(skills.router)
app.include_router(export.router)
app.include_router(settings.router)
app.include_router(goals.router)
app.include_router(profile.router)
app.include_router(learning.router)
app.include_router(backup.router)


@app.on_event("startup")
def on_startup():
    init_db()


FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"

if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

    @app.get("/{full_path:path}")
    def spa_fallback(full_path: str):
        return FileResponse(FRONTEND_DIST / "index.html")
