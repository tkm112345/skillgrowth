# Features

日本語版: [FEATURES.ja.md](FEATURES.ja.md)

## Dashboard

- **Career path goals** — three optional free-text boxes (this year / 5 years /
  10 years) for where you'd like to be heading. Each shows as read-only text
  with an Edit button; editing opens a draft you can Cancel (discarding the
  edit, reverting to what was last saved) or Save. Every saved change is
  kept as history — a "History (N)" link on each goal shows past versions
  with their dates, never overwritten.
- **Quick update** — a short free-text box for "what have you been working
  on lately"; submitting it runs skill extraction immediately, the same way
  every other activity source does.
- **Skill growth timeline** — a step-line chart of cumulative skill count
  over time, built from each skill's `first_observed_at`.
- **Category breakdown** — a bar chart of skill count per category.
- **Stats row** — total skills, category count, and skills added in the
  last 7 days. Placed at the bottom of the page by design — the growth
  timeline and goals are the point, the counters are secondary.

Turning these goals into LLM-backed suggestions happens on a separate
page — see **AI Integration** below — so the Dashboard itself never calls
an LLM.

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
skill extraction. Links do not — they're just facts, not activity to mine.

There's deliberately no "import resume" feature: a personal resume's layout
varies too much for reliable LLM extraction. Bulk-loading skills instead
goes through the CSV import on the Skills page.

## Skills

- The current skill picture, derived from the activity log: name, category,
  activity count, first-seen date, last-seen date.
- **Add a skill directly** by name/category, for skills you know you have
  but haven't produced activity for yet.
- **Import CSV** — bulk-add skills from a `name,category` CSV file
  (`category` column optional).
- Both paths are deduplicated case-insensitively against existing skills,
  and skills can also be deleted (the activity that mentioned them is kept).

## Activity

Both adding catch-up activity and browsing everything you've added live on
one page, since they were previously two overlapping screens (a Learning
Log page, and a read-only feed that already showed the same entries):

- **Add an activity** — reading, talk given, talk attended, certification,
  or other, each with a title, date, and notes. When the type is
  certification, an optional certificate image can be attached and is run
  through the same vision-based skill extraction as the Profile
  certification flow.
- **Feed** — a chronological view of every activity entry ever added (quick
  updates, certifications, the free-text side of every
  Education/Employment/Project entry, and the entries added above),
  labeled by source type. Loads 50 at a time with a "Load more" button,
  since this log only ever grows over the life of the app. (Manually added
  and CSV-imported skills don't appear here — they bypass the activity log
  entirely, since there's no free text behind them.)
- **Delete** — only shown on entries added through the form above; it
  removes that entry's structured type/title/date, while the entry itself
  stays in the feed as plain text, since the underlying activity log is
  append-only by design (the same as Education/Employment/Project
  deletions elsewhere in the app).

## Resume

- **Self PR** — a free-text pitch about yourself, included at the top of
  the generated resume. Adding one never overwrites the last: every entry
  is kept, so past drafts stay in history, and the resume always uses the
  most recent one.
- **Generate resume** — assembles the current skill picture, work/education
  history, and latest Self PR into Markdown, following a fixed set of
  sections (Self PR → Work History → Other Projects → Education → Skills →
  Certifications) — **no LLM involved**, just your existing data filled
  into that template, so it works even without an LLM configured. Rendered
  as formatted HTML in the UI (not raw Markdown text) and downloadable as a
  `.md` file. Every generation is kept as a snapshot, so past exports
  remain browsable (20 at a time, with a "Load more" button). Sections with
  no data are simply omitted.

## AI Integration

The only two features in the app that call an LLM at your request (activity
extraction also uses one, but that happens automatically as you add
activity, not from this page):

- **Growth guidance** — for any career path goal you've written on the
  Dashboard, the LLM suggests what to develop next given your current
  skills. Only calls the LLM for goals that actually have text; if none
  do, nothing is sent.
- **Job posting gap check** — paste a job description; the LLM compares it
  against your current skills and returns what you already meet, what's
  missing, and a short summary.

Keeping both under one page makes it obvious which parts of the app are
LLM-optional (everything else) versus LLM-required (just these two).

## Concept

An in-app page explaining the product's core loop and its four design
principles (self-hosted/single-user, free-text skills, pluggable LLM,
activity over self-assessment). The loop is drawn as a circle, not a
straight line: activity → extraction → skill picture → reflect (a
template-based resume, or optionally the AI Integration page's job gap
check / goal-based growth guidance) → back into what you check in about
next. Each pass around adds to the same accumulating skill picture rather
than starting over.

## Settings

- **Appearance** — language (English/Japanese), theme (System/Light/Dark),
  and an accent color picked from the app's 8-hue palette. All three are
  instant, client-side only (`localStorage`), and independent of each
  other — picking dark mode doesn't reset your accent color, and vice
  versa.
- **LLM connection** — base URL, API key, text model, vision model, stored
  in the database and editable from the UI — no `.env` editing or restart
  required. Works against any OpenAI-compatible chat completions endpoint:
  a cloud API or a local Ollama server.
- **Test connection** — sends a minimal request with the values currently
  in the form (not necessarily saved yet) and reports success or the exact
  error, so a typo in the API key or base URL is caught immediately instead
  of surfacing later as a failure somewhere else in the app. And if it does
  surface elsewhere (a quick update, a growth guidance request, a gap
  check), every LLM-backed endpoint returns the real failure reason as its
  error detail instead of a bare "Internal Server Error".
- **Data backup** — download every career record (activity, skills,
  profile, goals with their full history, links, self PR history, resume
  export history) as a single JSON file. Deliberately excludes the LLM
  connection settings (so an API key never ends up in a backup file).
- **Restore from backup** — upload a previously downloaded backup file to
  re-import its records. Always additive: it never deletes or overwrites
  existing rows, and only fills in a career goal if that horizon is still
  empty.
- **Sample data** — one click loads a small fictional career history
  (skills, quick updates, career goals, employment with nested projects,
  education, reading/talk/certification entries, links, a self PR entry, a
  resume snapshot) using the same import path as backup restore, so a
  fresh install can be explored without wiring up an LLM or typing
  anything in first — including generating a resume, since that no longer
  needs one. A matching **reset** button removes exactly what
  sample-loading added (tracked by id across every load, however many
  times you've run it) — anything you've entered yourself is left alone.
  Only the AI Integration page's two features still need a working LLM
  connection.
- **About this app** — opens a dialog with the app name and version
  (read from `/api/version`), the license, and a link to open a GitHub
  issue for bugs or feature requests.

## Cross-cutting

- **Collapsible sidebar** — the top bar's toggle button shrinks the sidebar
  to an icon rail; the state is remembered per browser.
- **Category/type color coding** — categories, activity types, and activity
  source types are each assigned one of 8 accent hues by a deterministic
  hash of their name, so the same category always gets the same color
  across the app without maintaining an explicit color list per page.
- **Version** — shown in the sidebar footer, read from the backend's
  `/api/version` (itself read from the repo's `VERSION` file), so it can
  never drift from what's actually deployed.
