# Repo+Story

**PR/repo-history narrative for review & maintenance.**

Repo+Story ingests a repository's git event-stream — commits × file mutations × authors,
the data Gource consumes, not its animation — and produces a clustered, blast-radius-aware
**story** in which every claim is cited back to its source commit. A Python/PyDriller
pipeline publishes it as a GitHub Action **sticky story** on the PR, so reviewers and
maintainers read what changed, why it matters, and what it touches — instead of re-deriving
it from raw history.

## Status

- Concept of record: idea **I1**, timerloggedout-spec/termux-monorepo
  `docs/ops/CHALLENGE-ENTRIES-LOG.md` §3 (PR #2481) — see [CONCEPT.md](CONCEPT.md).
- Spec: [SPEC.md](SPEC.md) (v1 seed; Delphi Oracle improvement pass ⇒ v2).
- Competition mapping: C8 Codegeist 2026 primary fit — **candidate only**; no registration
  or submission yet, and no claim beyond the mapping.
- ⚠ Not Repo Replay: a vastly different concept on ≈the same substrate. No shared engine.

## Layout

- `CONCEPT.md` — concept of record + provenance.
- `SPEC.md` — buildable spec derived from the concept.
