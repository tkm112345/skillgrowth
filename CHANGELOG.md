# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
The current version lives in the `VERSION` file. See `CLAUDE.md` for the
process this file follows (English only, updated as part of the same
commit as the change, moved into a dated section when a release is cut).

## [Unreleased]

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

[Unreleased]: https://github.com/tkm112345/skillgrowth/compare/v0.2.1...HEAD
[0.2.1]: https://github.com/tkm112345/skillgrowth/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/tkm112345/skillgrowth/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/tkm112345/skillgrowth/releases/tag/v0.1.0
