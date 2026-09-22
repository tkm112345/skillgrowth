# skillgrowth

Self-hosted career tracker that grows alongside your career, instead of
asking you to fill out a static profile once.

Every piece of evidence you feed it — a pasted resume, a certification
photo, a check-in note, an education/employment/project record, a learning
log entry — is kept as an append-only evidence log. An LLM extracts skills
from that evidence and matches them against skills you already have, so your
skill picture and a ready-to-use resume can be derived from the log at any
time.

```mermaid
flowchart LR
  U1[Resume import] --> E[(Evidence log)]
  U2[Quick check-in] --> E
  U3[Certification image] --> E
  U4[Education / Employment / Project] --> E
  U5[Learning log entry] --> E
  E --> L[LLM extraction + matching]
  L --> S[(Skill)]
  S --> V[Current skill view]
  S --> X[Resume export]
  S --> G[Job posting gap check]
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the full data model and
request flow.

## Features

- **Dashboard** — career path goals (this year / 5 years / 10 years,
  optional), a skill growth timeline chart, a category breakdown chart, and a
  quick check-in box.
- **Profile** — education, employment, and projects (standalone or linked to
  an employer). Free-text descriptions also feed skill extraction. A resume
  can be bulk-imported here to bootstrap the evidence log.
- **Learning log** — reading, talks given/attended, certifications (with
  optional certificate image upload for OCR extraction).
- **Skills** — the current skill picture derived from the evidence log; also
  supports adding a skill directly by name.
- **Evidence log** — a chronological feed of everything that has been added.
- **Export** — generates a resume (Markdown, rendered and downloadable) from
  the current skill picture, and a job-posting gap check (paste a job
  description to see which of its requirements you already meet).
- **Settings** — LLM connection (base URL / API key / model), stored in the
  database and editable from the UI.
- English by default, switchable to Japanese from the top bar.

## Design choices

- **Single user, self-hosted.** No auth, no multi-tenancy. Run your own
  instance the way you'd self-host a personal finance tool.
- **Free-text skills.** No fixed taxonomy. Skills are stored as the natural
  language the LLM extracts from your evidence (or that you type directly),
  not normalized IDs.
- **Pluggable LLM.** Talks to any OpenAI-compatible chat completions
  endpoint — a cloud API or a local Ollama server
  (`http://localhost:11434/v1`). Configured from the Settings page.
- **Evidence, not self-assessment.** Skills mostly come from things you
  already have (resume, certificates, project notes) rather than from
  filling out a skill matrix — though you can also add a skill by hand.

## Quick start

```bash
docker compose up --build
```

Open http://localhost:8000, then set your LLM connection under Settings.

## Local development

See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) for running the backend and
frontend separately with hot reload.

## Known limitations

- Certification ingestion accepts images only (no PDF parsing yet).
- Resume ingestion is paste-as-text (no PDF/Word upload yet).
- The "current skills" view is read from the database directly, but the
  match/merge step that keeps it deduplicated runs at evidence-ingestion
  time via an LLM call — quality depends on the configured model.

## License

MIT — see [LICENSE](LICENSE).
