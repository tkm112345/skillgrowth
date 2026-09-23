# Features

日本語版: [FEATURES.ja.md](FEATURES.ja.md)

> **Terminology:** every "skill" below is one of *your own* career/professional
> skills, not an AI "skill" (a Claude Code Skill, an LLM plugin, an agent
> capability). See the README's note on terminology.

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
- **Reflect** — a card showing what's changed (new skills, new activity,
  whether Vision or any career goal was edited) since you last marked
  yourself as having reflected, or everything so far if you never have.
  An "I reflected" button logs a new timestamp and resets the count to
  zero — a deliberately manual, explicit action rather than inferring
  "reflected" from an edit, so you can reflect (and decide nothing needs
  to change) without having to edit anything.
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
  labeled by source type and grouped under a year/month heading (e.g.
  "September 2026"). Loads 50 at a time with a "Load more" button, since
  this log only ever grows over the life of the app — groups are computed
  client-side from whatever's currently loaded, so a group can be partial
  until more is loaded. (Manually added and CSV-imported skills don't
  appear here — they bypass the activity log entirely, since there's no
  free text behind them.)
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

The only features in the app that call an LLM at your request (activity
extraction also uses one, but that happens automatically as you add
activity, not from this page):

- **Career Consult** — a chat with an AI career consultant grounded in
  your actual data: skills, activity, education, work history, Self PR,
  Vision, and career path goals are all sent as context on every message,
  so advice is specific to you rather than generic. Conversations are
  saved (a list of past ones, each with an auto-generated title from its
  first message, lives on this page) and can be resumed or deleted later.
  Unlike the two single-shot features below, this is a genuine multi-turn
  conversation — the full message history of a conversation is resent
  with every reply, so the AI keeps context as you go back and forth. If
  your message is saved but the AI's reply fails (e.g. a bad LLM
  connection), the message you wrote is never lost — only the reply
  fails.
- **Growth guidance** — for any career path goal you've written on the
  Dashboard, the LLM suggests what to develop next given your current
  skills. Only calls the LLM for goals that actually have text; if none
  do, nothing is sent.
- **Job posting gap check** — paste a job description; the LLM compares it
  against your current skills and returns what you already meet, what's
  missing, and a short summary.

Keeping all three under one page makes it obvious which parts of the app
are LLM-optional (everything else) versus LLM-required (just these
three).

## Concept

An in-app page opening with **why this exists** — career data usually
ends up on someone else's platform (a recruiter's site, an employer's
internal system) and was never really yours to keep, so skillgrowth
exists to put that record on your own server, built on your own
initiative rather than only when a job search or review forces the
question (see the README's "Why" section for the same explanation) —
followed by the product's core loop and its five design principles
(self-hosted/single-user, free-text skills, LLM-optional not
LLM-required, pluggable LLM, activity over self-assessment).

The loop is five steps, drawn as a circle for the first four with a
separate branch for the fifth:

1. **Vision** — sketch out, even roughly, the kind of career you want to
   build (on Vision or the Dashboard).
2. **Track** — keep recording and updating the skills and activity you
   actually have.
3. **Record** — education, work history, projects at work or in the open
   (OSS).
4. **Reflect** — revisit what you wrote in step 1, and think about what's
   still missing.

Step 4 flows straight back into step 1 — that's the main loop, and it's
the path drawn as a closed circle. Step 5 (**Prepare** — resume
generation, a job-posting gap check, growth guidance toward your goals,
and now a Career Consult conversation) is deliberately *not* part of that
circle: it's an occasional detour off of step 4, drawn as a separate
branch, not a step every pass through the loop takes. Its note that the
LLM-backed features here "haven't been thoroughly vetted yet" isn't about
them being unbuilt — all of them exist and work — it's a reliability
caveat: this app hasn't accumulated enough real-world use yet to vouch
for how good the LLM's suggestions actually are.

Many of this app's screens — Dashboard, Profile, Activity, Skills — are
different views onto that same append-only activity log, added to a
little at a time rather than reset each time around. Vision, career path
goals, Self PR, and resume generation itself all sit outside that log,
though, and never go through LLM extraction at any point.

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
  Only the AI Integration page's three features still need a working LLM
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
