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
- **Skill-improving actions per month** — a bar chart of how many pieces of
  evidence (`SkillLink` rows — checkins, learning activities,
  certifications, and anything else skill extraction ran against) were
  linked to a skill each month. Replaces an earlier cumulative
  skill-count timeline that reviewer feedback found less useful than
  seeing ongoing skill-building activity.
- **Category breakdown** — a bar chart of skill count per category.
- **Stats row** — total skills, category count, and skills added in the
  last 7 days. Placed at the bottom of the page by design — the action
  chart and goals are the point, the counters are secondary.

Turning these goals into LLM-backed suggestions happens on a separate
page — see **AI Career Support** below — so the Dashboard itself never calls
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

## Self Feedback

A dedicated page for structured, periodic self-review — its own entity
(`SelfFeedback`), separate from the activity log, not evidence-linked and
never run through skill extraction (like Vision and career path goals).
Replaced the Dashboard's old "Reflect" card, which only tracked a
timestamp and an optional free-text comment.

- **Add an entry** — a date (any date you choose; there's no imposed
  weekly/monthly structure) plus three side-by-side text areas: what you
  did, your thoughts/reflection on it, and what to carry forward next
  time. The Add button stays disabled until at least one of the three has
  something in it.
- **Past entries** — listed newest-first, each shown in the same
  three-column layout as the add form, loading 50 at a time with a "Load
  more" button. Unlike the append-only activity log, entries here can be
  fully **edited** (date and all three fields, via a dialog) or
  **deleted** — this is a personal journal, not an audit trail.

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

Education, Employment, and Project entries can each be edited in place
(fix a typo, correct a project's linked employer) as well as deleted —
editing never re-runs skill extraction, so it won't add or change linked
skills.

There's deliberately no "import resume" feature: a personal resume's layout
varies too much for reliable LLM extraction. Bulk-loading skills instead
goes through the CSV import on the Skills page.

## Portfolio

Deliverables and work samples — a Web link, a PDF, a spreadsheet, a
photo — kept separately from Profile's Education/Employment/Project
entries, so they can be shown to someone without those entries' baggage.

- Each item has a title, a free-text description (**not** run through
  skill extraction, unlike every other free-text field in this app), any
  number of links (label + URL), and any number of uploaded files —
  PDFs, spreadsheets (.xlsx/.xls/.csv/.ods), and photos
  (.jpg/.jpeg/.png/.gif/.webp), matching what this page is for. Each
  file is capped at 10MB.
- An item can optionally be linked to an existing Project from Profile —
  but **only a standalone project, never one tied to an employer**. This
  is enforced by the server, not just hidden from the dropdown, so a
  portfolio item can never end up identifying who you work for.
- Included in data backup/restore, with every uploaded file's actual
  content embedded (the same treatment Word resume templates get, since
  losing a deliberately-uploaded file on restore would be a real loss).

## Resume Import

Upload an existing resume (`.docx` only) and have the LLM draft
Education/Employment/Project/Certification/Self-PR entries from it, instead
of typing years of history in by hand.

- Nothing is saved until you review the draft and press Register. Each
  item has an on/off toggle and editable fields — turn off anything wrong
  or not worth keeping, fix typos or a project's linked employer first.
  The uploaded file itself is never stored.
- Registering creates entries through the same Profile/Certifications/
  Self-PR forms would, so the same rules apply as if you'd typed it in
  yourself.
- Skills the LLM could match to a specific project can be registered
  linked to that project (so they show up on the Skills page and in the
  Skill Network). A skill it couldn't tie to any project is shown as a
  reference-only tag instead — nothing with no activity behind it gets
  registered here, but you can always add it directly from the Skills page.
- Partial success is shown per item (e.g. one project failing doesn't
  stop the rest from registering).

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
- **Proficiency** — an optional 1-5 rating, set manually in the add/edit
  form (a 5-star picker that shows what each level means as you hover:
  aware / can do with guidance / can do independently / can apply and
  teach / go-to expert). Unlike everything else on this page, this one
  is a self-assessment rather than derived from activity — left unset
  (no stars shown) until you rate it yourself.
- Sample-data skills (see Settings' "Try it with sample data" below) are
  marked with a small "Sample" tag next to the skill name, so it's clear
  which rows came from the bundled sample data versus your own, even
  before you reset it.

## Activity

Both adding catch-up activity and browsing everything you've added live on
one page, since they were previously two overlapping screens (a Learning
Log page, and a read-only feed that already showed the same entries):

- **Add an activity** — pick a type, then a title, date, and notes. Types
  are user-managed via "Manage types" next to the field: the app seeds 5
  (reading, talk given, talk attended, certification, other), and any of
  them except certification can be renamed or deleted, and new ones added
  freely — deleting a type only removes it from the picker, existing
  entries keep their recorded type as plain text. Certification is the one
  built-in, protected type: it drives the resume's Certifications section
  and unlocks an optional certificate-image field (run through the same
  vision-based skill extraction as the Profile certification flow), so it
  can't be renamed or removed. Each certification also gets an **include
  in resume** switch, shown on its feed entry — same idea as Skills'
  switch of the same name, on by default — for keeping a certification
  tracked here without putting it in front of an employer.
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
- **Jump to month** — a dropdown, grouped by year with a count per month,
  built from a server-side aggregate rather than whatever happens to be
  loaded in the browser. Picking a month replaces the feed with just that
  month's entries (still paginated 50 at a time within it); clearing the
  selection returns to the normal newest-first feed. This is what makes
  jumping to an old month cheap even once the log has years of entries —
  the app never has to page through everything in between first.
- **Delete** — only shown on entries added through the form above; it
  removes that entry's structured type/title/date, while the entry itself
  stays in the feed as plain text, since the underlying activity log is
  append-only by design (the same as Education/Employment/Project
  deletions elsewhere in the app).
- **Certifications only** — a checkbox above the feed that filters it down
  to certification-type entries, sorted by their recorded date (newest
  first) instead of the feed's usual upload-time grouping; it filters
  whatever's currently loaded in the browser, so "Load more" may be needed
  first if an older certification isn't visible yet. Any entry with a
  recorded date (most visibly certifications) shows it under its text in
  the feed.
- Sample-data entries carry a small "Sample" tag next to their source-type
  label, same as on the Skills page.

## Certifications

A dedicated page, separate from the Activity feed's "Certifications only"
filter above, for managing certification entries one at a time:

- **List** — every certification entry, with its acquisition date, an
  optional expiry date, and the same "include in resume" switch shown on
  the Activity feed's certification entries (it's the same underlying
  field either way).
- **Add / edit** — a dialog for title, acquisition date, an optional
  expiry date, and notes. Editing is only available here — the Activity
  feed can delete a certification's structured fields but not edit them,
  so this is also how you backfill an expiry date on a certification
  added before this page existed.
- **Expired badge** — a certification whose expiry date is in the past is
  flagged with a red badge in the list. This is a visual cue only — there's
  no reminder or notification for an upcoming expiry.
- **Delete** — same behavior as the Activity feed: removes the structured
  type/title/date; the underlying activity log entry stays in the feed as
  plain text.

## Skill Network

A force-directed node/edge graph showing how your skills connect to the
career milestones that back them — which certifications, jobs, projects,
and education gave rise to which skills, and which projects belong to
which job or portfolio piece. Node size grows with how many connections a
node has. Clicking a node navigates to that entity's page (Skills,
Certifications, Profile, or Portfolio — there's no per-item deep link
since none of those pages have one yet).

Deliberately **not every activity is shown**: day-to-day entries (reading,
talks, quick updates) are excluded, since the activity log grows without
bound the longer you use the app and would turn the graph into an
unreadable tangle over time. Only inherently bounded milestones appear —
skills, certifications, education, employment, projects, and portfolio
pieces — so the graph stays legible no matter how long you've been using
skillgrowth.

Three display settings above the graph — label wrap width (characters
before a label line-breaks), node spacing, and edge length — are
adjustable and remembered per-browser (not synced to the account), since
how legible a given density of labels/nodes is depends on your screen and
how much data you have.

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
- **Word template export** — alongside the Markdown resume above, upload a
  `.docx` file with tags like `{{p self_pr }}` (an in-app reference panel
  lists all six available tags and the exact syntax they need) and
  generate a filled copy on demand — just as deterministic as the
  Markdown generator, no LLM involved. Multiple templates can be saved
  and switched between, with one marked as the default. Work history,
  projects, skills, and certifications can each be rendered as a bullet
  list or a native Word table — picked per template from a dropdown in
  the UI, not by editing the template file's own logic — so the same
  `.docx` design can show a table one way and a list another without
  keeping two separate template files.
- **Rirekisho** — a distinct document from the resume above: in Japanese
  job hunting, a rirekisho (履歴書) is a standardized personal-history form
  (name, contact details, a combined education/work-history table, a
  photo) separate from a shokumu-keirekisho (職務経歴書, what this app calls
  "Resume"). On the same page, a "Personal info" form holds name
  (+furigana), date of birth, postal code, address (+furigana), phone,
  email, and a photo upload. Below it, upload your own rirekisho-formatted
  `.docx` file with tags for that info plus education/work history (built
  from the same Education/Employment records as the resume, merged into
  one chronological table the way a rirekisho conventionally lists it),
  certifications, and Self PR — filled in on demand, same deterministic,
  no-LLM approach as the Word template export above. Deliberately **not**
  stored: gender, dependents, commute time, the "requests" column, and
  motivation for applying — each varies per application or is sensitive
  enough that a portable career record shouldn't hold it, so the uploaded
  template is expected to leave those for you to fill in by hand.

## AI Career Support

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
  fails. A "Customize this consultant" field (collapsed by default) lets
  you append your own instructions — tone, what to focus on — to the
  base system prompt. Deliberately scoped to Career Consult only: the
  other two AI features below parse a strict JSON shape out of the
  LLM's reply, so letting their prompts be freely edited risks breaking
  that parsing; Career Consult is free-form chat with nothing to break.
  An optional "Target industry" field, set when starting a conversation,
  asks the consultant to specialize its advice for that industry (using
  its own knowledge — no web search or external lookup involved); it's
  per-conversation rather than a global setting, so a manufacturing-focused
  conversation and an AI/IT-focused one can be kept side by side, shown as
  a small tag next to each conversation's title in the list.
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
4. **Reflect** — on Self Feedback, look back at what you did and what's
   still missing.

Step 4 flows straight back into step 1 — that's the main loop, and it's
the path drawn as a closed circle. Step 5 (**Prepare** — resume/rirekisho
generation, a job-posting gap check, growth guidance toward your goals,
and a Career Consult conversation) is deliberately *not* part of that
circle: it's an occasional detour off of step 4, drawn as a separate
branch, not a step every pass through the loop takes. Of those, only the
job-posting gap check, growth guidance, and Career Consult call an LLM;
resume and rirekisho generation are deterministic and don't. The in-app
note that the LLM-backed features here "haven't been thoroughly vetted
yet" isn't about them being unbuilt — all of them exist and work — it's a
reliability caveat: this app hasn't accumulated enough real-world use yet
to vouch for how good the LLM's suggestions actually are.

Many of this app's screens — Dashboard, Profile, Activity, Skills,
Certifications — are different views onto that same append-only activity
log, added to a little at a time rather than reset each time around.
Vision, career path goals, Self Feedback, Self PR, and resume/rirekisho
generation itself all sit outside that log, though, and never go through
LLM extraction at any point. Portfolio sits outside it too — its
description is deliberately excluded from skill extraction. Skill
Network isn't a view onto the log either — it visualizes how skills
relate to the other entities that back them.

## Settings

Split into four tabs — Appearance, LLM Connection, Data Management, and
About — since the flat list of cards this used to be had grown long
enough to be hard to scan.

- **Appearance** — language (English/Japanese), theme (System/Light/Dark),
  and an accent color picked from the app's 8-hue palette. All three are
  instant, client-side only (`localStorage`), and independent of each
  other — picking dark mode doesn't reset your accent color, and vice
  versa.
- **LLM connection** — base URL, API key, text model, vision model, stored
  in the database and editable from the UI — no `.env` editing or restart
  required. Works against any OpenAI-compatible chat completions endpoint:
  a cloud API or a local Ollama server. Once a key is set, the page never
  displays it again in plaintext — it shows a fixed placeholder instead,
  and saving other fields (or testing the connection) without retyping it
  reuses the stored key rather than overwriting it with the placeholder.
- **Skill extraction toggle** — a global on/off switch, **off by default**,
  covering the LLM call that extracts skills from Quick update, Activity,
  and Profile's free-text fields (education/employment/project). Off
  means those saves are instant with no LLM call; turn it on to get
  automatic skill extraction from free text, at the cost of waiting on
  the LLM for every save. Certification image extraction is a separate
  code path and always runs regardless of this switch.
- **Test connection** — sends a minimal request with the values currently
  in the form (not necessarily saved yet) and reports success or the exact
  error, so a typo in the API key or base URL is caught immediately instead
  of surfacing later as a failure somewhere else in the app. And if it does
  surface elsewhere (a quick update, a growth guidance request, a gap
  check), every LLM-backed endpoint returns the real failure reason as its
  error detail instead of a bare "Internal Server Error".
- **Data backup** — download every career record as a single JSON file:
  activity, skills, profile (education/employment/projects), goals with
  their full history, vision, self feedback, activity types, links,
  self PR history, resume export/template history, portfolio
  items/links/files, and Career Consult sessions. Deliberately excludes
  the LLM connection settings (so an API key never ends up in a backup
  file).
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
  Only the AI Career Support page's three features still need a working LLM
  connection.
- **Reset all data** — unlike the sample-data reset above, this wipes
  literally everything: your own data as well as sample data, and the LLM
  connection settings, back to exactly what a fresh install looks like.
  Fully irreversible, so it requires two confirmations — a warning dialog,
  then typing `RESET` — rather than the single confirm the other actions
  on this page use.
- **About this app** — opens a dialog with the app name, version (read
  from `/api/version`), and the license. Filing issues/PRs moved to the
  sidebar's Contribute button (see Cross-cutting below) so it's visible
  from every page, not just Settings.

## Cross-cutting

- **Installable (PWA)** — a web app manifest and service worker (via
  `vite-plugin-pwa`) let a mobile browser (Chrome/Safari) "Add to Home
  Screen," launching in its own standalone window with no browser UI.
  Only static assets (JS/CSS/HTML/icons) are precached — API requests
  stay network-only, since some features (LLM calls) are inherently
  online-only and there's nothing meaningful to serve offline for them.
- **Global search** — a search box in the top bar, on every page, matching
  keywords against Skills (name/category), Activity (title/notes), and
  Portfolio (title/description) via SQLite FTS5. Results are grouped by
  type with a short snippet; picking one navigates to that entity's page
  (Skills/Activity/Portfolio) and scrolls to/briefly highlights the
  matching row or card — on Activity's paginated, month-filterable feed,
  the month/certification filters are cleared and further pages are
  loaded (bounded) if the entry isn't already visible.
- **Collapsible, resizable sidebar** — the top bar's toggle button shrinks
  the sidebar to an icon rail; the state is remembered per browser.
  Defaults to collapsed on a first visit from a phone-width screen
  (≤768px), since the full sidebar otherwise eats roughly half the
  viewport there — once toggled either way, that explicit choice is
  what's remembered from then on, regardless of screen width. When
  expanded, its width can also be dragged from its right edge (remembered
  per browser too); the default width is wide enough that every nav label
  fits without truncating.
- **Category/type color coding** — skill categories and activity source
  types are each assigned one of 8 accent hues by a deterministic hash of
  their name, so the same category always gets the same color across the
  app without maintaining an explicit color list per page.
- **Version** — shown in the sidebar footer, read from the backend's
  `/api/version` (itself read from the repo's `VERSION` file), so it can
  never drift from what's actually deployed.
- **Contribute** — a prominent button sits just above the copyright line in
  the sidebar on every page, opening a dialog that links to the GitHub repo
  and points directly at filing an issue. skillgrowth is MIT-licensed and
  the intent is for this to be genuinely easy to find, not buried in
  Settings.
