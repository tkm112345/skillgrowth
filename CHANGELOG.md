# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
The current version lives in the `VERSION` file. See `CLAUDE.md` for the
process this file follows (English only, updated as part of the same
commit as the change, moved into a dated section when a release is cut).

## [Unreleased]

## [0.2.6] - 2026-09-26

### Added
- **Self Feedback**, a new page for structured periodic self-review: pick
  any date and write three things side by side — what you did, your
  reflection on it, and what to carry forward. Past entries are listed
  the same way, fully editable and deletable (`GET/POST /api/self-feedback`,
  `PUT/DELETE /api/self-feedback/{id}`), included in backup/restore.
- A demo GIF at the top of the README's Screenshots section, showing the
  Quick update → skill extraction → Skills page loop end to end.

### Removed
- The Dashboard's "Reflect" card (mark a timestamp, optional comment,
  browse history) — superseded by Self Feedback. The underlying
  `ReflectionLog` table and any existing reflections are **not**
  deleted (still included in backup/restore), just no longer written to
  or shown anywhere.

### Fixed
- The Self Feedback "Edit entry" dialog and the Activity page's "Manage
  types" dialog were both a fixed pixel width wider than a phone screen,
  cutting off their Save/Close buttons off-screen with no way to reach
  them. Both now cap at 92% of the viewport width.
- The Dashboard's "Career path goals" three columns (this year / 5 years /
  10 years) stayed side by side at any screen width, squeezing each
  column's Edit/History buttons into overlapping, unreadable text on a
  phone. Now stacks to one column below 768px; unchanged above it.

### Security
- Portfolio file uploads now only accept the file types the page is
  actually for (PDFs, spreadsheets, photos) instead of any file type.

### Changed
- The sidebar now defaults to collapsed on a first visit from a
  phone-width screen (≤768px) instead of always starting expanded — it
  was eating roughly half the viewport there. Once toggled either way,
  that explicit choice is remembered regardless of screen width, same as
  before.
- Added indexes on every foreign-key column (`SkillLink.evidence_id`/
  `skill_id`, `Education`/`Employment`/`Project`/`LearningActivity`'s
  `evidence_id`, `Project.employment_id`, `PortfolioItem.project_id`,
  `PortfolioLink`/`PortfolioFile.portfolio_item_id`,
  `ConsultMessage.session_id`) — a no-op on a fresh install, applied to
  existing installs' databases on next startup. Doesn't change behavior
  at today's data volumes; keeps lookups cheap as they grow.
- The list of existing skills sent to the LLM on every skill-extraction
  and Career Consult/gap-check/growth-guidance call is now capped at the
  300 most recently observed, instead of unbounded — keeps prompt
  size/latency from growing indefinitely over years of use.
- `docs/CONTRIBUTING.md` now sets expectations about response time
  (solo-maintained, no guaranteed turnaround).

## [0.2.5] - 2026-09-26

### Added
- `CODE_OF_CONDUCT.md` (Contributor Covenant), GitHub issue templates for
  bug reports and feature requests, a pull request template, and a
  contribution workflow (reporting bugs, opening PRs) documented in
  `docs/CONTRIBUTING.md`.
- A CI status badge in `README.md`.
- A `docker-publish` workflow that builds and pushes multi-arch
  (`linux/amd64`, `linux/arm64`) images to `ghcr.io/tkm112345/skillgrowth`
  on each tagged release, plus a `docker run` quick-start option in
  `README.md` for running that image without cloning the repo.
- `SECURITY.md`, documenting how to report a vulnerability and this
  project's scope (single-user self-hosted; no auth/multi-tenancy reports).
- A "Jump to month" dropdown on the Activity page, grouped by year with a
  count per month, backed by a new `GET /api/evidence/months` aggregate
  endpoint. Picking a month replaces the feed with just that month's
  entries (`GET /api/evidence` now also accepts `year`/`month` filters) —
  this scales to a long-running log without having to page through
  everything in between to reach an old month.
- Activity types are now user-managed instead of a fixed list. A "Manage
  types" dialog on the Activity page lets you add, rename, and delete
  types (`GET/POST /api/learning/types`, `PUT/DELETE
  /api/learning/types/{id}`); the app still seeds the same 5 defaults on
  first run. "Certification" stays a built-in, protected type, since it
  drives the resume's Certifications section and the certificate-image
  upload field — it can't be renamed or deleted. Deleting a custom type
  only removes it from the picker; activities already recorded with it
  keep it as plain text. Included in backup/restore.

### Security
- `GET /api/settings` no longer returns the LLM API key in plaintext; it's
  masked in responses, and saving/testing settings without changing it now
  reuses the stored key server-side instead of requiring it to be retyped.
- Certification image evidence uploads (`POST /api/evidence/image`) now
  enforce the same 10MB size limit as portfolio file uploads, closing a
  disk-exhaustion gap where that endpoint had no limit at all.
- The Docker image now runs the app as a non-root user instead of root.
  A `docker-entrypoint.sh` chowns `/app/data` to that user on every
  container start before dropping privileges (via `gosu`), so installs
  upgrading from the old always-root image keep working even though their
  existing data directory was created by root.

### Fixed
- The Resume page's "Word template" section (upload a .docx template, fill
  it with current data) was silently missing from every render. A literal
  `{{p self_pr }}` example in the hint text broke vue-i18n's message
  compiler, which threw before the section could mount; the example is now
  escaped so it renders as intended.
- The Profile page's "Other projects" section had no empty-state message
  when it had no entries, unlike Education, Work history, and Links right
  next to it.
- The sidebar collapse/expand button had no accessible name (icon-only,
  no `aria-label`), so screen reader users couldn't tell what it did.
- Vision and Career path goals showed a "Last updated" timestamp even when
  nothing had ever been saved (the API synthesized a fresh timestamp for an
  unsaved default row). Both now return `null` until an actual save happens.
- The Concept page's "core loop" diagram: step 1's label text overlapped the
  card header on narrower renders.
- The Skills page showed two redundant empty-state messages ("No Data" from
  the table plus a separate illustration) when no skills were recorded yet.

### Changed
- The Dashboard's "New here?" link is now a more visible pill-style button
  instead of small inline text.
- Added a short clarifying hint to the "Quick update" and "Career path
  goals" cards on the Dashboard, since their overlap with the Activity page
  and the Vision page respectively wasn't obvious at a glance.
- Bumped the base font size (13px → 16px, and Element Plus's small variant
  12px → 14px) — the previous size read as slightly small.
- The Portfolio "Add deliverable" dialog and the Activity page's "Add an
  activity" form used a fixed label-width narrow enough that the larger
  font size above made longer labels ("Linked project (optional)",
  "Certificate image (optional)") wrap awkwardly mid-word. Both forms now
  put labels above their fields instead of beside them.
- Clarified the "Linked project" hint on the Portfolio "Add deliverable"
  dialog to say where to create a linkable project (Profile → "Other
  projects") — it previously only described the filter rule (no employer
  tie), not where such a project comes from.

## [0.2.4] - 2026-09-24

### Added
- Backend linting/formatting with [ruff](https://docs.astral.sh/ruff/) and
  frontend linting with ESLint, unified behind `make check` (and `make
  lint` for a faster subset) and enforced in CI. See
  `docs/CONTRIBUTING.md`.
- A Claude Code `PreToolUse` hook (`.claude/hooks/protect_db.py`) that
  blocks Bash commands which would delete/overwrite
  `data/skillgrowth.db` while the app container is running, plus two
  Claude Code skills (`release-cutting`, `schema-migration`) that carry
  the step-by-step procedures previously spelled out in full in
  `CLAUDE.md`.

### Security
- CI now runs [`invisible-unicode-check`](https://github.com/tkm112345/invisible-unicode-check)
  on every pull request, blocking merges that introduce invisible or
  adversarial Unicode (GlassWorm-style payload encoding, Trojan Source).
- Dependabot is configured for pip, npm, Docker base images, and GitHub
  Actions, with a 7-day cooldown before a newly published version is
  proposed, to avoid pulling in a version before a supply-chain
  compromise in it would typically be caught.

## [0.2.3] - 2026-09-24

### Added
- A new Portfolio page for tracking deliverables and work samples: each
  item has a title, a free-text description (deliberately not run through
  skill extraction), any number of links, and any number of uploaded files
  (PDF, spreadsheets, photos, etc. — no extension restriction, 10MB per
  file). An item can optionally link to an existing Project, but only a
  standalone one not tied to an employer — enforced server-side, not just
  hidden in the UI — so a portfolio item can never identify who you work
  for. Included in data backup/restore, with uploaded file content
  embedded like Word resume templates.
- Word template resume export: upload a `.docx` file with tags like
  `{{p self_pr }}` (see the in-app tag reference on the Resume page) and
  generate a filled copy on demand — deterministic, no LLM involved, same
  as the existing Markdown resume generator which it runs alongside.
  Multiple templates can be saved and switched between. Work history,
  projects, skills, and certifications can each be rendered as a bullet
  list or a native Word table, chosen per template from the UI. Included
  in data backup/restore (with the template file itself embedded, unlike
  certificate images).
- A "Reflect" card on the Dashboard: shows what's changed (new skills,
  new activity, whether Vision or any career goal was edited) since you
  last marked yourself as having reflected, or everything so far if you
  never have. An "I reflected" button logs a new timestamp and resets
  the count — a deliberately explicit action, not inferred from editing
  anything. Included in data backup/restore. Fills the "Reflect" step of
  the Concept page's core loop, which previously had no feature behind
  it.
- Reflect entries can now carry an optional comment, and a "History"
  link browses past reflections (date + comment), 5 at a time.
- A global "skill extraction" toggle in Settings, **off by default**:
  when off, Quick update, Activity, and Profile's free-text fields save
  instantly with no LLM call; turn it on for automatic skill extraction
  from that text, at the cost of waiting on the LLM for every save.
  Certification image extraction is unaffected either way.

## [0.2.2] - 2026-09-23

### Added
- Screenshots in README.md (Dashboard, Skills, Activity, Resume), captured
  against the built-in sample data.
- A terminology note in README.md and both FEATURES docs clarifying that
  "skill" throughout this app means the user's own career/professional
  skill, not an AI/agent "skill" such as a Claude Code Skill.
- The Activity feed now groups entries under a year/month heading (e.g.
  "September 2026") instead of one flat chronological list.

### Removed
- `.env.example` and all env-var-based LLM configuration plumbing
  (`load_dotenv()` in `app/main.py`, `env_file` in `docker-compose.yml`,
  the `python-dotenv` dependency). Nothing in the app read those variables
  any more — LLM connection settings have lived in the database, edited
  from the Settings page, since that feature was added; the `.env`-based
  docs and wiring were stale leftovers from before that.

## [0.2.1] - 2026-09-22

### Added
- A "Why" section on both the Concept page and README.md explaining the
  problem skillgrowth actually solves: career history usually ends up on
  someone else's platform (a recruiter's site, an employer's internal
  system) and was never really yours to keep — skillgrowth exists so you
  can own and keep building that record yourself, on your own server, on
  your own initiative.
- README.md documents confirmed-working example LLM configurations
  (OpenAI, Ollama, Claude, Gemini) with base URLs and provider-specific
  caveats, plus a note that neither Anthropic nor OpenAI allow
  third-party apps to authenticate via a consumer subscription login —
  an API key is the only option for any provider.
- Career Consult: a saved, multi-turn chat with an AI career consultant
  on the AI Integration page. Every message sends the full conversation
  history plus a context block built from your skills, activity,
  education, work history, Self PR, Vision, and career path goals, so
  advice is grounded in real data rather than generic. Conversations
  persist (list, resume, delete) and are included in data backup/restore.
  If the AI's reply fails, the message you sent is never lost — it's
  committed before the LLM is even called.
- Resume snapshots can be edited directly as Markdown after generation, in
  place, with an `edited_at` timestamp shown alongside the original
  generation date.
- Self PR entries can be edited in place, and any past entry can be
  explicitly selected as the one used in the generated resume — not just
  whichever is newest.
- Skills can be edited (name/category) directly from the Skills page, and
  each skill has an "include in resume" switch controlling whether it
  appears in a generated resume, independent of everywhere else it's
  still tracked.
- A lightweight schema-migration helper (`app/db.py::_ensure_column`) so
  a column added to an existing model doesn't crash already-deployed
  instances the next time it's written to.
- GitHub repository topics (`self-hosted`, `career`, `career-development`,
  `skill-tracking`, `resume-builder`, `fastapi`, `vuejs`, `sqlite`).
- Project-level `CLAUDE.md` and this changelog.

### Changed
- The Concept page's core loop and design principles were rewritten to
  reflect that the app is LLM-optional, not LLM-premised: a new fifth
  principle ("LLM-optional, not LLM-required") was added, and the loop
  diagram now notes it's skipped entirely for a direct skill add or CSV
  import, with career path goals / Vision / Self PR / resume generation
  sitting outside the loop altogether.
- The Concept page's core loop content itself was reworked into five
  steps (Vision → Track skills/activity → Record education/work/projects
  → Reflect against your Vision → Prepare for your next career move), and
  its shape changed from a single closed circle to a 4-step main loop
  (step 4 flows back to step 1) with step 5 drawn as a separate,
  occasional branch off of step 4 rather than a step every pass takes.
- The tagline was reframed from "grows alongside your career" to "grows
  together with you," to make the tool's relationship to the person using
  it, not just their career data, explicit.
- The sidebar's GitHub issue/PR encouragement moved out of Settings'
  "About this app" dialog into a dedicated, prominent "Contribute" button
  above the sidebar's copyright line, visible from every page.

### Fixed
- Two accuracy issues found in a self-review of the Concept page rework
  above: growth guidance was missing from step 5's description even
  though it's one of only two AI Integration features (job-posting gap
  check was the only one mentioned); and the loop's note about the
  append-only activity log incorrectly listed Vision as one of the
  screens backed by it — Vision is deliberately outside that log
  entirely, same as career path goals, Self PR, and resume generation.
  Also clarified that step 5's "LLM-backed features haven't been
  thoroughly vetted yet" is a reliability caveat about the gap check and
  growth guidance specifically (not enough real-world use yet to vouch
  for suggestion quality) — not a claim that they don't exist. Both are
  already built and working, same as resume generation (which was never
  LLM-backed to begin with).
- Resume generation would crash (`no such column`) on any instance that
  had already generated a resume before this change, because
  `ExportSnapshot.edited_at` was added to an existing table with no way
  to backfill it on upgrade. Fixed by the migration helper above.

## [0.2.0] - 2026-09-22

### Added
- Vision page: one free-form, unstructured box for a rough sketch of the
  career you're aiming for, separate from the Dashboard's three
  time-boxed career path goals.
- Career path goals gained an explicit edit mode (Cancel reverts a draft,
  Save commits it) and full, paginated edit history.
- Self PR field on the Resume page, with paginated history.
- AI Integration page: growth guidance and job-posting gap check, split
  out from Dashboard/Resume so it's the only page that calls an LLM on
  demand.
- Settings: Appearance (language, light/dark/system theme, an accent
  color from the app's 8-hue palette), a dedicated LLM connection card,
  and an About panel (version, license).

### Changed
- Resume generation is fully LLM-free: your data is filled into a fixed
  Markdown template, so it works even without an LLM configured.
- The Activity page absorbs what used to be a separate Learning Log page
  — add a reading/talk/certification entry and browse the full activity
  feed in one place.
- Renamed "Evidence Log / 証拠ログ" to "Activity / アクティビティ"
  throughout the UI and docs.

### Fixed
- The sidebar app icon silently failed to load — a static-file-serving
  bug in the SPA fallback route was returning `index.html` for
  `/favicon.svg` instead of the actual file.
- Theme color changes had no visible effect in dark mode — a CSS
  specificity conflict against Element Plus's own dark stylesheet.

## [0.1.0] - 2026-09-22

Initial tagged release: a self-hosted career tracker that grows alongside
your career.

### Added
- Append-only evidence log with LLM-based skill extraction and matching.
- Dashboard: career path goals, skill growth timeline, category
  breakdown, quick updates, goal-based growth guidance.
- Profile: education, employment (with nested projects), standalone
  projects, external links.
- Learning log with certificate image OCR.
- Skills: manual add, CSV import.
- Resume generation and job-posting gap check.
- Settings: pluggable LLM connection with a test button, JSON data
  backup and restore, one-click sample data.
- English/Japanese UI.

[Unreleased]: https://github.com/tkm112345/skillgrowth/compare/v0.2.3...HEAD
[0.2.3]: https://github.com/tkm112345/skillgrowth/compare/v0.2.2...v0.2.3
[0.2.2]: https://github.com/tkm112345/skillgrowth/compare/v0.2.1...v0.2.2
[0.2.1]: https://github.com/tkm112345/skillgrowth/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/tkm112345/skillgrowth/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/tkm112345/skillgrowth/releases/tag/v0.1.0
