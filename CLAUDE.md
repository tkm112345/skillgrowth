# CLAUDE.md

Project-specific rules for working in this repository. Keep this file
short — put anything long in `docs/` and link to it from here.

## Language

- **Conversation with the user in this repo**: match whatever language
  they're writing in — for personal development sessions that's usually
  Japanese.
- **Everything written to the repository or to GitHub** — commit
  messages, `CHANGELOG.md` entries, PR titles/descriptions, GitHub
  release notes, code comments — is always **English**, regardless of
  what language the conversation itself is in. This repo is public and
  MIT-licensed; its artifacts should be readable by anyone, not just the
  maintainer.

## Before committing

1. `pytest -q` (backend, from the repo root) and `npm run build` (from
   `frontend/`) both pass.
2. If the `app` service in `docker-compose.yml` is currently running,
   rebuild it (`docker compose up --build -d`) and smoke-test the change
   with `curl` against the live container. This has caught real bugs the
   test suite alone missed — schema migrations especially (see below).
3. Update `docs/FEATURES.md` **and** `docs/FEATURES.ja.md` together for
   any user-facing change — they're parallel documents and must never
   drift out of sync with each other. Update `docs/ARCHITECTURE.md`
   (English only, no Japanese counterpart) for any backend/data-model
   change. `README.md`'s feature list and "Usage" section are a shorter
   mirror of `FEATURES.md`, not a separate source of truth.
4. If the change belongs in a release, add it under `CHANGELOG.md`'s
   `## [Unreleased]` section as part of the same commit — don't let the
   changelog fall behind and try to reconstruct it later.

## Commit attribution

Every commit in this repo, including ones Claude Code makes on the
user's behalf, is pushed under the repo owner's own GitHub account
(`tkm112345`, already the configured git identity — don't change it).
Do **not** append a `Co-Authored-By: Claude Sonnet 5 <...>` (or any
other AI-attribution) trailer to commit messages in this repo, even
though that's Claude Code's usual default — commits here should read as
authored solely by the repo owner.

## Never delete `data/skillgrowth.db` while the container is running

The app runs against a bind-mounted SQLite file. Deleting or truncating
it while `docker compose up` is live corrupts the running instance (this
happened once — it produced `no such table` errors mid-session). Stop the
container first (`docker compose stop`), or simply don't touch the file
while `up --build` is running.

## Schema changes: there is no migration tool

There's no Alembic (or anything else). `SQLModel.metadata.create_all()`
(called from `app/db.py::init_db()`) only creates *tables* that don't
exist yet — it never alters a table that's already on disk.

**Any new column added to an existing model needs a matching
`app/db.py::_ensure_column(engine, table, column, ddl_type)` call inside
`init_db()`.** Skip this and every self-hosted instance that already has
that table crashes the moment the column is first written to — a fresh
install is fine (`create_all()` gives it the full current schema), an
upgraded one is not. A brand new table needs no such call; `create_all()`
handles that case correctly on its own. This actually happened once
(`ExportSnapshot.edited_at`) — see `docs/ARCHITECTURE.md`'s "Schema
changes with no migration tool" section for the full incident and the
fix.

## Versioning and releases

- The version lives in the `VERSION` file — bump it by hand, don't infer
  it from git tags or commit count. `VERSION` tracks the version being
  worked toward, not the last released one — see the release cycle below.
- `CHANGELOG.md` follows [Keep a Changelog](https://keepachangelog.com/).
  Add entries under `## [Unreleased]` as changes are made, not batched up
  right before a release. English only (see "Language" above), even in
  an otherwise-Japanese session.
- Release cycle: `VERSION` is bumped to the next version immediately
  after each tag is pushed (last bullet below), so by the time you cut a
  release `VERSION` already holds the version being released — no bump
  needed at cut time, unless what shipped turned out to need a bigger
  bump than the placeholder chosen right after the previous tag (e.g.
  minor instead of patch), in which case adjust `VERSION` by hand before
  cutting.
- Cutting a release: move the `Unreleased` content into a new dated
  version section in `CHANGELOG.md` matching the current `VERSION`,
  commit, then `git tag vX.Y.Z` and `gh release create vX.Y.Z` with
  release notes built from the same changelog entry (see prior releases
  for the "Highlights" format).
- Immediately after tagging and creating the release, bump `VERSION` to
  the next version in its own commit (e.g. "Bump version to 0.2.3") —
  every commit from that point on is already working toward the next
  release, not still showing the one that just shipped.
- This repo pushes directly to `main` (no PR workflow) and branch
  protection is bypassed by the repo owner — that's expected, not an
  error to work around.
