# skillgrowth

Self-hosted career tracker that grows alongside your career, instead of
asking you to fill out a static profile once.

Every piece of activity you feed it — a quick update, a certification
photo, an education/employment/project record, a reading/talk/certification
entry — is kept as an append-only activity log. An LLM extracts skills
from that activity and matches them against skills you already have, so
your skill picture and a ready-to-use resume can be derived from the log
at any time — the resume itself is generated from a fixed template, no
LLM required. Skills can also be added directly (one at a time, or in bulk
via CSV) when you don't have free-text activity to extract from.

```mermaid
flowchart LR
  U1[Quick update] --> E[(Activity log)]
  U2[Certification image] --> E
  U3[Education / Employment / Project] --> E
  U4[Reading / talk / certification entry] --> E
  U5[Manual add / CSV import] --> S[(Skill)]
  E --> L[LLM extraction + matching]
  L --> S
  S --> V[Current skill view]
  S --> X[Resume export - no LLM]
  S --> G[AI Integration: job gap check / growth guidance]
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the full data model and
request flow.

## Features

Full feature list: [docs/FEATURES.md](docs/FEATURES.md) ([日本語](docs/FEATURES.ja.md)).

- **Dashboard** — career path goals (this year / 5 years / 10 years,
  optional, editable with a full history of past edits), a skill growth
  timeline chart, a category breakdown chart, and a quick update box.
- **Profile** — education, employment, and projects (standalone or linked to
  an employer). Free-text descriptions also feed skill extraction.
- **Skills** — the current skill picture derived from the activity log; also
  supports adding a skill directly by name, or importing a batch from a
  `name,category` CSV file — deliberately not resume parsing, since a
  personal resume's layout is too format-dependent for reliable extraction.
- **Activity** — add a reading/talk/certification entry (with optional
  certificate image upload for OCR extraction) and browse a chronological
  feed of everything that's been added, in one page.
- **Resume** — a Self PR field (kept as history, most recent used) plus a
  resume generator that fills a fixed Markdown template from your current
  data — **no LLM involved**, rendered and downloadable, with past
  generations kept as browsable snapshots.
- **AI Integration** — the only two features that call an LLM on demand:
  growth guidance toward each Dashboard goal, and a job-posting gap check
  (paste a job description to see which of its requirements you already
  meet).
- **Settings** — language, theme (light/dark/system) and an accent color,
  the LLM connection (base URL / API key / model, with a test button), a
  full data backup download, restoring from a backup file, and an About
  panel with the app version, license, and a link to file issues.

## Design choices

- **Single user, self-hosted.** No auth, no multi-tenancy. Run your own
  instance the way you'd self-host a personal finance tool.
- **Free-text skills.** No fixed taxonomy. Skills are stored as the natural
  language the LLM extracts from your activity (or that you type directly),
  not normalized IDs.
- **Pluggable LLM.** Talks to any OpenAI-compatible chat completions
  endpoint — a cloud API or a local Ollama server
  (`http://localhost:11434/v1`). Configured from the Settings page.
- **Activity, not self-assessment.** Skills mostly come from things you
  already have (certificates, project notes, a CSV export from wherever you
  already track this) rather than from filling out a skill matrix — though
  you can also add a skill by hand.

## Quick start

```bash
docker compose up --build
```

Open http://localhost:8000, then set your LLM connection under Settings.
Want to see what a populated app looks like first? Settings → "Try it with
sample data" loads a small fictional career history with one click.

## Local development

See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) for running the backend and
frontend separately with hot reload.

## Known limitations

- Certification ingestion accepts images only (no PDF parsing yet).
- No resume/CV parsing by design — see "Design choices" above.
- The "current skills" view is read from the database directly, but the
  match/merge step that keeps it deduplicated runs at evidence-ingestion
  time via an LLM call — quality depends on the configured model.
- Generated resumes follow a fixed set of sections and aren't customizable
  per-export; edit the downloaded Markdown by hand for anything beyond that.

## License

MIT — see [LICENSE](LICENSE).
