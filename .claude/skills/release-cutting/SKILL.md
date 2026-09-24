---
name: release-cutting
description: Cut a new skillgrowth release — move CHANGELOG.md's Unreleased section into a dated version, tag it, publish the GitHub release, and bump VERSION for the next cycle. Use when asked to cut/ship a release or tag a version.
---

# Cutting a release

Prerequisite context (see `CLAUDE.md`'s "Versioning and releases" for the
parts that apply year-round, not just at cut time): `VERSION` already
holds the version being released by the time you get here — it was bumped
to it right after the *previous* tag was pushed. Only adjust `VERSION` by
hand first if what actually shipped needs a bigger bump than the
placeholder chosen back then (e.g. it turned out to be a minor change,
not a patch).

## Steps

1. In `CHANGELOG.md`, move the `## [Unreleased]` content into a new dated
   section matching `VERSION`, e.g.:
   ```
   ## [0.2.4] - 2026-09-24
   ```
   (Keep an empty `## [Unreleased]` heading above it for the next round of
   changes.)
2. Commit that change (this repo pushes directly to `main`, no PR — see
   `CLAUDE.md`).
3. Tag and publish:
   ```bash
   git tag v0.2.4
   git push origin main
   git push origin v0.2.4
   gh release create v0.2.4 --title v0.2.4 --notes "..."
   ```
   Build the release notes from the same changelog entry, in a
   "Highlights" format — bullet the handful of most user-visible changes
   in plain prose, then point to the full lists. Real example
   (`gh release view v0.2.3`):
   ```
   Fifth tagged release of skillgrowth.

   **Highlights**
   - New Portfolio page for tracking deliverables and work samples —
     title, description (not fed into skill extraction), any number of
     links, and any number of uploaded files (10MB each, no extension
     restriction). Can optionally link to a standalone project, but never
     one tied to an employer — enforced server-side, so a portfolio item
     can never identify who you work for.
   - Word template resume export: upload a `.docx` file with tags like
     `{{p self_pr }}` and generate a filled copy on demand, alongside the
     existing Markdown generator — deterministic, no LLM involved.
     Multiple templates can be saved and switched between, with
     per-section bullet-list/table layout chosen from the UI.

   See [CHANGELOG.md](https://github.com/tkm112345/skillgrowth/blob/v0.2.3/CHANGELOG.md)
   for the full list, and [FEATURES.md](https://github.com/tkm112345/skillgrowth/blob/v0.2.3/docs/FEATURES.md)
   for the complete feature list.
   ```
4. **Immediately after**, in its own commit, bump `VERSION` to the next
   version (e.g. "Bump version to 0.2.5") — every commit from this point
   on is already working toward the next release.

## Notes

- Don't batch steps 1–4 into one commit; step 2's commit is the release
  itself, step 4's is the start of the next cycle.
- `VERSION` is bumped by hand, never inferred from git tags or commit
  count.
