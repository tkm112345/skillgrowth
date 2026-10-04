# Roadmap: reaching v1.0.0

skillgrowth is currently `0.x` — under [SemVer](https://semver.org/),
that means "anything may still change," and this project has used it
that way: most releases so far have been additive feature drops, cut
as patch bumps regardless of size (see `CLAUDE.md`'s "Versioning and
releases" for the patch-vs-minor rule now in effect going forward).

`v1.0.0` is a deliberate milestone, not something that falls out
automatically from a version-bump rule. It marks the point where the
core feature set is considered done, and upgrading an existing
self-hosted install is treated as a real compatibility commitment
rather than "probably fine, hasn't broken yet."

## Checklist

- [ ] **Core loop is feature-complete.** The pages that make up the
  Concept page's five-step loop (Vision → track skills/activity →
  record education/work/projects → reflect against Vision → prepare for
  the next career move — Dashboard, Vision, Self Feedback, Profile,
  Skills, Activity, Certifications, Portfolio, Skill Network, Export,
  AI Career Support)
  are all in place, and recent releases have stopped adding *new
  pages/nav items* — only refinements to what's already there.
  **Not yet** (checked 2026-10-04): the most recent release, 0.4.0,
  added a new nav item (Resume Import), so this hasn't held true for
  even one full release cycle yet.
- [x] **Self-hosting operational basics are in place.** Health check
  (`GET /api/health`, done), an optional access gate for internet-facing
  instances (`SKILLGROWTH_BASIC_AUTH_*`, done), PWA installability
  (done) — the baseline for "I can run this on my own server and
  trust it to behave." Verified 2026-10-04: all three present in
  `app/main.py`, `app/basic_auth.py`, and `frontend/vite.config.js`'s
  `VitePWA` setup.
- [x] **Schema migrations stay additive-only.** `app/db.py`'s
  `_ensure_column`/`_ensure_index` approach (see
  `docs/ARCHITECTURE.md`'s "Schema changes with no migration tool") has
  never required a destructive change so far — 1.0 is where this
  becomes an explicit promise for existing installs' upgrade path, not
  just incidental practice. Verified 2026-10-04: every call in
  `app/db.py` adds a column/index; `CHANGELOG.md` has no `ALTER`/`DROP`
  or other destructive schema entry in its history.
- [ ] **Docs match reality.** `README.md`, `docs/FEATURES.md` /
  `FEATURES.ja.md`, `docs/ARCHITECTURE.md`, `docs/CONTRIBUTING.md`, and
  `SECURITY.md` accurately describe what's actually implemented, with
  no stale sections left over from removed/changed features.
  **Partially audited 2026-10-04**: cross-checked all five files
  against `app/routers/`, `app/models.py`, `frontend/src/router`, and
  `Makefile`; found and fixed two drifts (README's stale "no resume/CV
  parsing" claim, and a missing rirekisho mention in the backup
  description — see `CHANGELOG.md`). Left unchecked because the audit
  wasn't exhaustive line-by-line across all of `ARCHITECTURE.md`'s 1000+
  lines, and screenshots/OpenAPI docs weren't cross-checked.
- [x] **CI is consistently green.** `make check` passes on `main`, and
  dependency updates (Dependabot) are being kept current rather than
  piling up. Verified 2026-10-04: latest CI run on `main` is green, zero
  open PRs (`gh pr list`), and the last 10 Dependabot PRs were all
  merged same-day or within days of opening.

## Not a hard requirement, but worth weighing

- **External usage signal** — someone other than the maintainer running
  it, filing an issue, opening a PR, or the project appearing somewhere
  like awesome-selfhosted (tracked separately as OpenProject milestones
  `#895`/`#896`). This is a traction signal, not a technical readiness
  one — a project can be technically 1.0-ready with zero outside users,
  and this project's `v1.0.0` decision doesn't have to wait on it. It's
  listed here because it's a common informal bar other maintainers use
  before calling something 1.0, not because this project requires it.

## What v1.0.0 changes going forward

Once cut, the major digit becomes the real breaking-change gate:
`### Added` entries keep landing as minor releases per `CLAUDE.md`'s
rule, but anything that would break an existing install on upgrade — a
destructive schema change, a backup/restore format break, removing a
working feature or endpoint without a replacement, a Docker/env
requirement that breaks existing deployments — bumps the major version
instead, called out prominently in that release's notes.
