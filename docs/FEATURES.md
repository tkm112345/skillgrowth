# Features

日本語版: [FEATURES.ja.md](FEATURES.ja.md)

## Dashboard

- **Career path goals** — three optional free-text boxes (this year / 5 years /
  10 years) for where you'd like to be heading. Each shows as read-only text
  with an Edit button; editing opens a draft you can Cancel (discarding the
  edit, reverting to what was last saved) or Save. Every saved change is
  kept as history, never overwritten — a "History" link on each goal
  lazy-loads past versions with their dates, 5 at a time with a "Load more"
  link, so the page stays light even after years of edits.
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

## Vision

A single free-text box for a rough, unstructured sketch of the kind of
career you're aiming for — no horizons, no required shape, just whatever
comes to mind. Deliberately looser than the Dashboard's three career path
goals: goals ask "what, by when," Vision doesn't ask anything. There's one
value (a singleton, not a list), shown pre-filled with whatever was last
saved and overwritten in place on Save — unlike career path goals, past
versions aren't kept as history. Like career path goals, it's plain text
with no LLM involvement (extraction or otherwise) and doesn't appear in
the Activity feed.

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
- Both paths are deduplicated case-insensitively against existing skills.
- **Edit** a skill's name or category directly — useful for fixing an
  LLM extraction mistake (a typo, a category you'd rather it sat under)
  without deleting and re-adding it. Renaming to a name that collides
  with a different existing skill (case-insensitively) is rejected rather
  than silently merging the two.
- Skills can also be **deleted** (the activity that mentioned them is kept).
- **Include in resume** — a switch on each row controls whether that skill
  appears in the "Skills" section of a generated resume. On by default;
  useful for keeping something in your tracked skill picture without
  putting it in front of an employer (an old technology you're not looking
  for work in, a soft skill that doesn't read well as a bare list item,
  etc.). Turning it off doesn't delete or hide the skill anywhere else in
  the app — only the resume template respects it.

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
  is kept as history, paging in 10 at a time with a "Load more" button
  (same as resume snapshots below). A newly-added entry automatically
  becomes the one used in the resume, but any past entry can be picked
  instead via "Use this version" — so writing a new draft doesn't force
  you to use it yet. Each entry can also be **edited** in place (fixing a
  typo doesn't need a whole new entry), and the entry currently feeding
  the resume is marked "In use."
- **Generate resume** — assembles the current skill picture, work/education
  history, and the selected Self PR into Markdown, following a fixed set of
  sections (Self PR → Work History → Other Projects → Education → Skills →
  Certifications) — **no LLM involved**, just your existing data filled
  into that template, so it works even without an LLM configured. Rendered
  as formatted HTML in the UI (not raw Markdown text) and downloadable as a
  `.md` file. Every generation is kept as a snapshot, so past exports
  remain browsable (20 at a time, with a "Load more" button). Sections with
  no data are simply omitted.
- **Edit a snapshot** — any past resume, not just the latest, can be edited
  directly as raw Markdown (an "Edit" toggle switches the rendered view to
  a textarea) and saved back in place. Useful for polishing wording the
  template can't get exactly right, or tailoring one snapshot for a
  specific application without generating a fresh one. An edited snapshot
  shows both when it was generated and when it was last edited.

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
  profile, goals with their full history, vision, links, self PR history,
  resume export history) as a single JSON file. Deliberately excludes the
  LLM connection settings (so an API key never ends up in a backup file).
- **Restore from backup** — upload a previously downloaded backup file to
  re-import its records. Always additive: it never deletes or overwrites
  existing rows, and only fills in a career goal if that horizon is still
  empty.
- **Sample data** — one click loads a small fictional career history
  (skills, quick updates, career goals, a vision, employment with nested
  projects, education, reading/talk/certification entries, links, a self
  PR entry, a resume snapshot) using the same import path as backup restore, so a
  fresh install can be explored without wiring up an LLM or typing
  anything in first — including generating a resume, since that no longer
  needs one. A matching **reset** button removes exactly what
  sample-loading added (tracked by id across every load, however many
  times you've run it) — anything you've entered yourself is left alone.
  Only the AI Integration page's two features still need a working LLM
  connection.
- **About this app** — opens a dialog with the app name, version (read
  from `/api/version`), and the license. Filing issues/PRs moved to the
  sidebar's Contribute button (see Cross-cutting below) so it's visible
  from every page, not just Settings.

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
- **Contribute** — a prominent button sits just above the copyright line in
  the sidebar on every page, opening a dialog that links to the GitHub repo
  and points directly at filing an issue. skillgrowth is MIT-licensed and
  the intent is for this to be genuinely easy to find, not buried in
  Settings.
