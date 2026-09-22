from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

load_dotenv()

from app.db import init_db  # noqa: E402
from app.llm import LLMRequestError  # noqa: E402
from app.routers import backup, evidence, export, goals, learning, profile, settings, skills  # noqa: E402

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


@app.on_event("startup")
def on_startup():
    init_db()


FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"

if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

    @app.get("/{full_path:path}")
    def spa_fallback(full_path: str):
        return FileResponse(FRONTEND_DIST / "index.html")
