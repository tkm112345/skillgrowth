# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
The current version lives in the `VERSION` file. See `CLAUDE.md` for the
process this file follows (English only, updated as part of the same
commit as the change, moved into a dated section when a release is cut).

## [Unreleased]

### Added
- CI now runs [`gitleaks`](https://github.com/gitleaks/gitleaks) on every
  push and pull request, scanning full git history for committed secrets
  (API keys, tokens, private keys).

## [0.5.0] - 2026-10-05

### Added
- Certification upload (Activity page) and Resume Import now accept
  `.pdf` in addition to their existing formats. A certification `.pdf`
  has its first page rasterized to an image and goes through the same
  vision-based extraction as an uploaded image; Resume Import reads a
  `.pdf`'s embedded text (no OCR, so a scanned/image-only PDF is
  rejected the same way an empty `.docx` already was). New dependency:
  `pymupdf` (a pure wheel, no system packages needed).
- Skills page: a skill not seen in 180+ days now gets a "Stale" tag next
  to its last-seen date, the same visual pattern Certifications already
  uses for an expired certification.
- Certifications page: a new "Considering / Planned" tab tracks
  certifications you're considering or scheduled to take, separate from
  the existing "Acquired" tab. A "Mark as acquired" action converts a
  candidate into a regular certification entry (through the same
  evidence/skill-extraction path manual entry uses) and removes it from
  the candidates list.
- Bookmarks: a new page for saving links with a manually-entered title
  and an optional memo — no automatic title fetching, no LLM/evidence
  involvement, just a flat list you manage yourself.
- Optional MCP server: set `SKILLGROWTH_MCP_ENABLED=1` to mount an MCP
  server at `/mcp` (off by default) so an MCP client can read and add your
  career data through conversation. Covers read/add/update across
  activity, certifications (including candidates), bookmarks, skills,
  profile, portfolio, self feedback, self PR, goals, and vision —
  deliberately no delete operations, Settings, backup, LLM-only
  endpoints, or file uploads. Respects the existing Basic Auth gate when
  both are enabled. New dependencies: `fastapi-mcp`, `mcp` (pinned below
  2.0 for compatibility).

### Fixed
- README's "Known limitations" no longer claims "no resume/CV parsing by
  design", which contradicted the Resume Import feature described earlier
  in the same file; replaced with the actual limitation (`.docx` only, no
  PDF or other formats).
- `docs/FEATURES.md`/`FEATURES.ja.md`'s Settings backup description now
  lists rirekisho personal info/templates, which `POST /api/backup/export`
  already includes but the docs had omitted.

## [0.4.0] - 2026-10-03

### Added
- Resume Import: upload an existing resume (`.docx`) and let the LLM draft
  Education/Employment/Project/Certification/Self-PR entries from it. The
  draft is never auto-saved — each item is reviewed, edited, and confirmed
  individually before being created through the same endpoints manual
  entry uses, so existing invariants apply automatically. A skill the LLM
  could match to a specific project in the resume can be registered linked
  to that project (showing up in Skills and the Skill Network); a skill it
  couldn't tie to any project is shown for reference only.
- Education, Employment, and Project entries on the Profile page can now be
  edited in place, not just added and deleted.

### Changed
- Skill Network node labels are a bit larger (11px → 14px) for legibility,
  and its label wrap width, node spacing, and edge length are now
  adjustable (remembered per-browser) instead of fixed.

### Fixed
- Skill extraction's category for a newly created skill now matches the
  language of the text it was extracted from, instead of always defaulting
  to Japanese category labels (e.g. "技術") regardless of what language a
  quick update, evidence entry, or profile description was written in.
- A skill's "last seen" date is now updated when the LLM matches it by
  `skill_id` (reusing an existing skill it was given the id for), not just
  when it's matched by name — previously that case silently left "last
  seen" stale even though a new activity/evidence link for the skill was
  being recorded.

## [0.3.2] - 2026-10-03

### Security
- Backup restore now re-checks the "portfolio items may only link to a
  standalone project" rule before restoring a `PortfolioItem`, dropping the
  association instead of restoring it as-is. Restoring a hand-edited backup,
  or one taken before this rule existed, could otherwise bypass the
  server-side check and recreate a portfolio item pointing at an
  employer-tied project.

### Fixed
- Evidence-based skill extraction no longer creates a case-insensitive
  duplicate skill (e.g. "python" alongside an existing "Python") when the
  LLM match response omits `skill_id`. It now reuses the existing skill via
  the same name-matching path already used by manual skill creation and CSV
  import.
- `PUT /api/goals/{horizon}` now rejects a horizon outside the fixed
  this_year/5_years/10_years set (400) instead of silently creating a
  permanently invisible goal row; backup restore applies the same check.

## [0.3.1] - 2026-09-30

### Added
- The sidebar can now be resized by dragging its right edge (the width
  is remembered across sessions). The default width is also wider than
  before, so labels like "Self Feedback" (セルフフィードバック) aren't
  clipped by the fixed-width ellipsis.

### Changed
- The sidebar's brand title is a bit larger (0.95rem → 1.1rem, with the
  logo mark scaled up to match) for better legibility.

### Fixed
- Settings' page-level description ("Configure the LLM connection...")
  was shown under every tab (Appearance, Data Management, About), not
  just LLM Connection; moved it under that tab's own card instead.
- Personal info photo upload and evidence image upload now reject
  extensions outside an image allowlist (matching the existing Portfolio
  upload check), closing a gap where an uploaded `.svg` could be
  rendered inline by the browser instead of as a plain image. The
  evidence-image Vision LLM call also now maps `.gif`/`.webp` to their
  correct MIME type instead of mislabeling every non-PNG upload as JPEG.
- `GET /api/skills/{id}` for an unknown id now returns 404 instead of a
  raw 500 (a response-model validation error, since every other Skill
  endpoint already 404s on a missing id but this one didn't check).
- "Reset all data" now also deletes personal-info photo, evidence image,
  and rirekisho-template files from disk — it previously only cleared
  Portfolio and resume-template uploads, leaving the rest behind despite
  the DB rows for them being gone.
- Skills, Certifications, Profile (education/employment/project/link),
  Dashboard (goal/quick-update), Activity, Resume/Rirekisho (personal
  info, photo, templates, exports, Self PR), and Portfolio forms now
  show an error message when a save, delete, or download request fails,
  instead of failing silently (the dialog/form just sat there with no
  feedback and only a console error).
- Picking a result from the top-bar search now scrolls to and briefly
  highlights the matching skill/portfolio item/activity entry, instead
  of only opening its list page (which could leave you to hunt for it
  yourself, especially on Activity's paginated feed).

## [0.3.0] - 2026-09-27

### Added
- Rirekisho (履歴書) generation, on the Resume page: a "Personal info" form
  (name, date of birth, address, phone, email, a photo) plus your own
  rirekisho-formatted `.docx` template upload, filled in with that info
  and your existing education/work history, certifications, and Self PR —
  the same deterministic, no-LLM approach as the existing Word template
  export, but for the standardized Japanese personal-history form, which
  is a distinct document from this app's existing resume
  (shokumu-keirekisho) generator. Gender, dependents, commute time, the
  "requests" column, and motivation for applying are deliberately not
  stored, since each varies per application or is sensitive with little
  value in a portable career record — left for the template to leave
  blank for hand-filling.
- A "Connections" page: a force-directed node/edge graph of how skills
  connect to the certifications, education, employment, projects, and
  portfolio pieces that back them. Deliberately excludes day-to-day
  activity entries (reading, talks, quick updates) — the activity log
  grows without bound, and including it would turn the graph into an
  unreadable tangle over time.
- An optional HTTP Basic Auth gate, off by default: set
  `SKILLGROWTH_BASIC_AUTH_USER` and `SKILLGROWTH_BASIC_AUTH_PASS` to
  require that username/password on every request except `/api/health`
  (kept open so the Docker `HEALTHCHECK` doesn't start failing). Leaves
  the app fully unauthenticated when unset, as before — for anyone
  exposing their instance to the internet rather than a local
  network/VPN and wanting a minimal gate without a reverse proxy.
- PWA support (`vite-plugin-pwa`): an installable web app manifest and a
  service worker that precaches static assets only, so a mobile browser
  can "Add to Home Screen" and launch skillgrowth without browser UI. API
  requests stay network-only.
- An optional "Target industry" field when starting a Career Consult
  conversation, asking the consultant to specialize its advice for that
  industry using its own knowledge (no web search or tool use involved).
  Set per-conversation rather than as a global setting, so a
  manufacturing-focused conversation and an AI/IT-focused one can be kept
  side by side — shown as a small tag next to each conversation's title.
- A global search box in the top bar, matching keywords across Skills,
  Activity, and Portfolio (SQLite FTS5), grouped by type with a snippet;
  picking a result navigates to that entity's page.
- A dedicated Certifications page (new sidebar entry), listing every
  certification with its acquisition date and an optional expiry date
  (flagged with a badge once past), and letting you edit or delete an
  entry directly — including backfilling an expiry date onto a
  certification added before this page existed, which the Activity feed
  has no way to do.
- A `GET /api/health` endpoint (200 with a live DB connection, 503
  otherwise) and a Docker `HEALTHCHECK` that polls it, so container
  orchestrators, reverse proxies, and uptime monitors can check liveness
  without hitting an unrelated endpoint.
- A "Customize this consultant" field on the AI Integration page (Career
  Consult), appended to the base system prompt — tone, focus areas,
  anything to always keep in mind. Scoped to Career Consult only: the
  other two AI features parse a strict JSON shape out of the LLM's
  reply, so a user-edited prompt there risks breaking that parsing;
  Career Consult is free-form chat with nothing to break.
- A "Certifications only" filter on the Activity feed, sorting matches by
  their recorded date instead of upload time. Any activity with a
  recorded date now also shows it under its feed entry.
- Backend logging to a rotating file at `data/logs/app.log` (5MB per
  file, 5 backups kept), so unhandled-exception tracebacks survive past
  the container's live console output.
- An optional 1-5 proficiency rating on each skill, set manually from the
  Skills page's add/edit form (a star picker that shows what each level
  means as you rate it). Left unset until rated.
- A "Sample" tag on skills and Activity feed entries that came from
  "Try it with sample data," so they're distinguishable from your own
  data before you reset it.
- A "Reset all data" action on the Settings page, wiping everything
  (your own data, sample data, and the LLM connection settings) back to
  a fresh install. Irreversible, so it requires a warning dialog and
  then typing `RESET` to confirm.

- An "include in resume" switch on each certification (Activity feed),
  mirroring Skills' switch of the same name — resume_builder.py's
  Certifications section now respects it.

### Fixed
- A Career Consult session's "Target industry" was exported in a data
  backup but silently dropped on restore — the field existed on the
  model but the backup importer's `ConsultSession` construction never
  read it back out.
- Adding a certification from the Activity page tagged its feed entry as
  generic "Learning" rather than "Certification" — only the separate
  certificate-image upload path got the right tag. Every other activity
  type (reading, talk given/attended, other, custom types) already
  showed the correct generic tag and is unaffected.
- The sidebar was narrow enough that a longer nav label ("Self Feedback")
  triggered a horizontal scrollbar inside it; widened the sidebar and
  fixed the underlying overflow-x gap so this can't recur for any label.
- The certification row in Activity's "Manage types" dialog had its label
  competing for space with its full-sentence hint the same way a label
  competes with two short buttons on every other row, squeezing the hint
  into a cramped column instead of letting it wrap normally.

### Changed
- The sidebar's 13 flat nav items are now grouped into 5 collapsible
  categories (Overview, Direction, Activity & Skills, Background,
  Output), plus a standalone Settings entry — it had grown hard to scan.
  "Connections" is renamed "Skill Network" and "AI Integration" is
  renamed "AI Career Support," both purely cosmetic (no route/behavior
  change).
- The Settings page is split into four tabs (Appearance, LLM Connection,
  Data Management, About) instead of a long flat stack of cards, for the
  same reason.
- The Concept page's loop and design-principle text is corrected to
  match the app as it exists now: the "LLM features aren't thoroughly
  vetted yet" caveat no longer reads as if it covers resume/rirekisho
  generation (both are LLM-free); step 5 and the loop note now mention
  rirekisho generation and Certifications; the note clarifies Portfolio
  and Skill Network sit outside the append-only activity log rather than
  being another view onto it; the self-hosted principle now mentions the
  optional Basic Auth gate; the activity-over-self-assessment principle
  now notes skill proficiency as its one deliberate exception.
- The Dashboard's skill growth timeline (a step-line chart of cumulative
  skill count) is replaced with a bar chart of skill-improving actions
  per month — reviewer feedback found the cumulative count less useful
  than seeing ongoing skill-building activity. `GET /api/skills/timeline`
  is replaced by `GET /api/skills/action-counts`.
- A fresh install's LLM text/vision model fields now start empty instead
  of pre-filled with `gpt-4o-mini` — a hardcoded default reads as stale
  the moment a provider retires or renames it, and it wasn't going to age
  any better than that one did. The Settings page still shows it as a
  placeholder/example; leaving it unset surfaces the provider's own
  "model is required" error clearly rather than silently trying a name
  that may no longer exist.

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
