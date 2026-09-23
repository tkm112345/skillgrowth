from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.db import init_db
from app.llm import LLMRequestError
from app.routers import (
    ai,
    backup,
    consult,
    evidence,
    export,
    goals,
    learning,
    profile,
    reflection,
    self_pr,
    settings,
    skills,
    vision,
)

VERSION = (Path(__file__).resolve().parent.parent / "VERSION").read_text().strip()

app = FastAPI(title="skillgrowth", version=VERSION)


@app.exception_handler(LLMRequestError)
def handle_llm_request_error(request: Request, exc: LLMRequestError) -> JSONResponse:
    return JSONResponse(status_code=502, content={"detail": f"LLM request failed: {exc}"})


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
app.include_router(ai.router)
app.include_router(self_pr.router)
app.include_router(vision.router)
app.include_router(consult.router)
app.include_router(reflection.router)


@app.on_event("startup")
def on_startup():
    init_db()


FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"

if FRONTEND_DIST.exists():
    DIST_ROOT = FRONTEND_DIST.resolve()
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

    @app.get("/{full_path:path}")
    def spa_fallback(full_path: str):
        # Serves files copied into dist from frontend/public (favicon.svg,
        # icons.svg, ...) directly; anything else falls back to index.html
        # so client-side routing can take over.
        candidate = (DIST_ROOT / full_path).resolve()
        if full_path and candidate.is_file() and candidate.is_relative_to(DIST_ROOT):
            return FileResponse(candidate)
        return FileResponse(FRONTEND_DIST / "index.html")
