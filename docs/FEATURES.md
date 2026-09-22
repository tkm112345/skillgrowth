# Features

日本語版: [FEATURES.ja.md](FEATURES.ja.md)

## Dashboard

- **Career path goals** — three optional free-text boxes (this year / 5 years /
  10 years) for where you'd like to be heading. Saved on blur, never
  required.
- **Quick update** — a short free-text box for "what have you been working
  on lately"; submitting it runs skill extraction immediately, the same way
  every other evidence source does.
- **Skill growth timeline** — a step-line chart of cumulative skill count
  over time, built from each skill's `first_observed_at`.
- **Category breakdown** — a bar chart of skill count per category.
- **Stats row** — total skills, category count, and skills added in the
  last 7 days. Placed at the bottom of the page by design — the growth
  timeline and goals are the point, the counters are secondary.
- **Growth guidance** — for any goal you've written, the LLM suggests what
  to develop next given your current skills. Only calls the LLM for goals
  that actually have text.

## Profile

- **Links** — a small list of label+URL pairs for showing your public work
  and presence: GitHub, X, note, Zenn, a personal blog or homepage, or
  anything else. No fixed platform list — the label is free text.
- **Education** — school, degree, major, start/end date, free-text
  achievements.
- **Employment** — company, department, role, start/end date (leave end
  date blank for a current position).
- **Projects** — title, role, start/end date, free-text description.
  Optionally linked to an employer (nested under it in the UI) or
  standalone (personal projects, freelance work, etc.).

All free-text fields here (achievements, project descriptions) also feed
skill extraction. Links do not — they're just facts, not evidence to mine.

There's deliberately no "import resume" feature: a personal resume's layout
varies too much for reliable LLM extraction. Bulk-loading skills instead
goes through the CSV import on the Skills page.

## Learning Log

Tracks catch-up activity outside of formal work history:

- **Reading**, **talk given**, **talk attended**, **certification**, **other**
  — a fixed set of activity types, each with a title, date, and notes.
- When the type is **certification**, an optional certificate image can be
  attached; it's sent through the same vision-based skill extraction used
  for the Profile certification flow.

## Skills

- The current skill picture, derived from the evidence log: name, category,
  evidence count, first-seen date, last-seen date.
- **Add a skill directly** by name/category, for skills you know you have
  but haven't produced evidence for yet.
- **Import CSV** — bulk-add skills from a `name,category` CSV file
  (`category` column optional).
- Both paths are deduplicated case-insensitively against existing skills,
  and skills can also be deleted (the evidence that mentioned them is kept).

## Evidence Log

A chronological, read-only feed of every evidence entry ever added —
quick updates, certifications, and the free-text side of every
Education/Employment/Project/Learning Log entry — labeled by source type.
(Manually added and CSV-imported skills don't appear here — they bypass the
evidence log entirely, since there's no free text behind them.) Loads 50 at
a time with a "Load more" button, since this log only ever grows over the
life of the app.

## Resume

Both features here are about how you look to an employer, so they live
under one heading rather than a generic "Export":

- **Generate resume** — assembles the current skill picture into a
  Markdown resume via the LLM. Rendered as formatted HTML in the UI (not
  raw Markdown text) and downloadable as a `.md` file. Every generation is
  kept as a snapshot, so past exports remain browsable (20 at a time, with
  a "Load more" button).
- **Job posting gap check** — paste a job description; the LLM compares it
  against your current skills and returns what you already meet, what's
  missing, and a short summary.

## Concept

An in-app page explaining the product's core loop and its four design
principles (self-hosted/single-user, free-text skills, pluggable LLM,
evidence over self-assessment). The loop is drawn as a circle, not a
straight line: evidence → extraction → skill picture → reflect (resume
export, job gap check, or goal-based growth guidance) → back into what you
check in about next. Each pass around adds to the same accumulating skill
picture rather than starting over.

## Settings

- **LLM connection** — base URL, API key, text model, vision model, stored
  in the database and editable from the UI — no `.env` editing or restart
  required. Works against any OpenAI-compatible chat completions endpoint:
  a cloud API or a local Ollama server.
- **Test connection** — sends a minimal request with the values currently
  in the form (not necessarily saved yet) and reports success or the exact
  error, so a typo in the API key or base URL is caught immediately instead
  of surfacing later as a failure somewhere else in the app. And if it does
  surface elsewhere (a check-in, a resume generation, a gap check), every
  LLM-backed endpoint returns the real failure reason as its error detail
  instead of a bare "Internal Server Error".
- **Data backup** — download every career record (evidence, skills,
  profile, goals, learning log, links, resume export history) as a single
  JSON file. Deliberately excludes the LLM connection settings (so an API
  key never ends up in a backup file).
- **Restore from backup** — upload a previously downloaded backup file to
  re-import its records. Always additive: it never deletes or overwrites
  existing rows, and only fills in a career goal if that horizon is still
  empty.
- **Sample data** — one click loads a small fictional career history
  (skills, quick updates, career goals, employment with nested projects,
  education, learning log, links, a resume snapshot) using the same import
  path as backup restore, so a fresh install can be explored without
  wiring up an LLM or typing anything in first. A matching **reset**
  button removes exactly what sample-loading added (tracked by id across
  every load, however many times you've run it) — anything you've entered
  yourself is left alone. Generating a resume or running the job-gap/growth
  checks still needs a working LLM connection, since sample data only
  seeds the database, not the LLM-backed features.

## Cross-cutting

- **Internationalization** — English by default, switchable to Japanese
  from the top bar (vue-i18n). The choice is remembered per browser.
- **Collapsible sidebar** — the top bar's toggle button shrinks the sidebar
  to an icon rail; the state is remembered per browser.
- **Light/dark mode** — follows the OS/browser preference automatically.
- **Version** — shown in the sidebar footer, read from the backend's
  `/api/version` (itself read from the repo's `VERSION` file), so it can
  never drift from what's actually deployed.
