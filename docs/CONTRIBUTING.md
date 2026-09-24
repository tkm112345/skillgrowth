# Local development

Running the backend and frontend separately gives you hot reload on both
sides. This is the recommended way to work on the app; `docker compose up`
is for running a built instance, not for iterating on code.

## Backend

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --reload --port 8000
```

The backend serves the API at `/api/*`. It will also try to serve
`frontend/dist` if that directory exists (see `app/main.py`) — during
development you generally won't have built it, so `/` will 404 from the
backend alone. That's expected; use the frontend dev server (below) for the
UI.

The SQLite database is created at `data/skillgrowth.db` on first run. Delete
it to reset all data.

## Frontend

```bash
cd frontend
npm install
npm run dev
```

This starts the Vite dev server (default port 5173) with hot module
reload. `vite.config.js` proxies `/api/*` to `http://127.0.0.1:8000`, so run
the backend first. Open the Vite dev server URL, not the backend's port, for
day-to-day frontend work.

## Building for production

```bash
cd frontend && npm run build
```

This writes static assets to `frontend/dist`. Once built, the backend alone
(`uvicorn app.main:app`) serves the full app on one port — this is what the
`Dockerfile`'s multi-stage build does.

## Linting and type-checking

```bash
make check
```

Runs everything CI checks: backend lint/format (`ruff check .`, `ruff
format --check .`), backend tests (`pytest -q`), frontend lint (`npm run
lint`, from `frontend/`), and the frontend build. Run `make lint` alone to
skip the slower test/build steps. Individual commands also work directly
(`.venv/bin/ruff check .`, `cd frontend && npm run lint`, etc.) if you only
need one of them.

## Project layout

```
app/              FastAPI backend
  models.py       SQLModel table definitions
  db.py           engine, session, singleton Settings bootstrap
  llm.py          all LLM calls (extraction, matching, resume, gap check)
  services.py     shared evidence→skill-extraction logic
  routers/        one file per resource (evidence, skills, profile, ...)
frontend/         Vue 3 SPA
  src/views/      one component per route
  src/locales/    en.json / ja.json (vue-i18n)
  src/api.js      thin fetch wrapper for the backend API
docs/             this file, ARCHITECTURE.md
```

## Adding a new evidence-backed record type

If you're adding something similar to Education/Employment/Project/
LearningActivity (a structured record whose free-text fields should also
feed skill extraction), follow the existing pattern in
`app/routers/profile.py`:

1. Add the SQLModel table in `app/models.py` with an optional
   `evidence_id` foreign key to `EvidenceEntry`.
2. In the router's create endpoint, build a text blob from the record's
   free-text fields with `services.text_block(...)`, call
   `services.record_evidence_and_extract(...)` to create the `EvidenceEntry`
   and run skill extraction, then save the record with the returned
   `evidence_id`.
3. Add the corresponding `source_type` to the comment in
   `EvidenceEntry.source_type` and to the label maps in
   `frontend/src/locales/*.json` (`timeline.source*`).
