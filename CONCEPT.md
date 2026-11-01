# Repo+Story — Concept of Record

<!-- Seed v1.1: I1 of record + Gemini verbatim fold-in (2026-11-01, Gemini lane 107af1b2). Manager: Repo-Story — Manager · Oversight (chat 8cc20168). -->

## Provenance

- Idea bank **I1**, `docs/ops/CHALLENGE-ENTRIES-LOG.md` §3, timerloggedout-spec/termux-monorepo @master
  (log blob `71a051d482aabd0c3311e96d3c8829b0091b33cb`, verified firsthand 2026-11-01; master head `82241ffbea0c` at seed time).
- Landed via PR **#2481**, merged `3deacc54bf` (2026-10-30).
- Source: owner, 2026-10-30; Google AI Mode share `share.google/aimode/FWlvGfxlRa556mbGr` (read firsthand 2026-10-30).
- Name: **Repo+Story** (owner name); the source conversation titles it "PR+Story" — one concept, two titles.
- Full text: `docs/GEMINI-CONCEPT-VERBATIM.md` in this repo — the AI Mode conversation verbatim
  (5 prompts + 5 responses, 2026-10-30), fetched 2026-11-01 by the Gemini web lane. Exhaustive
  Gemini search found NO second/branch version: this share IS the single concept source, and
  I1 is its faithful compression (Δ below).
- ⚠ Repo+Story ≁ Repo Replay: vastly different concepts on ≈same substrate (git/repo history,
  provenance, session-export data). No shared engine, no shared entry (owner law, 2026-10-30).

## I1 concept (of record, near-verbatim)

- **Surface:** GitHub App *(I1's label — corrected by Δ1 below)*.
- **Ingest:** the git event-stream — commits × file mutations × authors — the data Gource
  consumes, *not* its animation.
- **Transform:** clustered, blast-radius-aware narrative where **every claim is cited ↦ its
  source commit**.
- **Pipeline:** Python / PyDriller ⇒ GitHub Action that posts a **sticky story** (PR surface).
- **Persistence (candidate set, undecided in I1):** `.story/` JSON · vector index · SQL chrono-graph.
- **Goal:** make repo-history / PR maintenance easy — a reviewer/maintainer reads the story of
  what changed, why it matters, and what it touches, instead of re-deriving it from raw history.

## Concept in full (Gemini verbatim, folded in)

- **Premise (owner prompt 2, correcting response 1):** "Not the Gource animations; the sources
  it uses, to generate story context… making repo history | PR etc maintenance easier." The
  R1 visual-playback/D3-treemap framing was DISCARDED by that correction — not concept.
- **Narrative model:** chronological evolution, not a static diff — Iteration Path
  (change → rewrite → revert = architectural dead-end story); Blast Radius (co-changing file
  clusters = implicit dependencies); Why-behind-What (commit messages × line diffs = auditable
  trail); strict markdown citations `[Desc](commit_hash)`.
- **Pipeline:** Git Event Stream → Context & Clustering Engine (noise filter: lockfiles,
  linters · cluster API+Test+Docs · rename lineage) → Narrative Generation Layer. Python-first:
  PyDriller (+ Isomorphic-Git, GitPython noted); scripts `extract_pr_story_context` and
  `mine_pr_evolution` (file-coupling matrix; payload {metadata, chronological_stream,
  architectural_coupling}); a "technical code chronicler" system prompt drives narration.
- **Features:** Impact Areas alerts · Automated Changelogs with Receipts · Contextual Blame ·
  blast-radius maintenance warning (e.g. `routes/user.py` changed without `tests/test_user.py`).
- **Persistence (prompt 5, "Mechanisms"):** M1 `.story/` PR-{id}.json (git-native: orphan
  refs/notes/stories) · M2 ChromaDB local vector DB (`.story_vector_db`, collection
  `repo_history_stories`) · M3 SQL chrono-graph (Commits/FileMutations/Coupling tables,
  `shared_commit_count` smell flag) · **recommended hybrid:** merge → Action → central
  datastore → coupling alerts → pinned Story.

## Δ vs I1 (of record)

- **∅Δ:** premise, narrative model, PyDriller pipeline, persistence trio, sticky Action, goal.
- **Δ1 SURFACE (material):** I1 says "GitHub App surface" — the Gemini text specifies **no
  App**. Surfaces of record = **GitHub Action + pre-push hook + pinned Story comment** (§
  Surfaces in SPEC.md). The App label survives only as I1's compression artifact, flagged here.
- **Δ2:** the Gemini text is a superset: full code/YAML/prompts/features verbatim (I1 = 1 line).
- **Δ3:** R1 visual playback = discarded draft framing (see Premise).

## Competition mapping (claims gated)

- **C8 Codegeist 2026** (Atlassian, Devpost) — PRIMARY fit. Submissions close Dec 22, 2026,
  3:00 PM ET. Entry requires a Forge app + ≥1 Atlassian product (Bitbucket/Jira/Confluence/
  Rovo/Teamwork Graph); category: Apps for Software Teams ("smarter code reviews" ∈ brief);
  demo video <5 min; install link for judges.
- C9 Gemma 4 △ and C10 Agentware △ are alternates only.
- Status of record: **candidate** — no slate insertion, no registration, no submission yet.
  Eligibility ≠ claim; no C8 claim language beyond this mapping until an entry exists.
