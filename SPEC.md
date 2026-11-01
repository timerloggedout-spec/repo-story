# Repo+Story — Spec v1.1 (seed + Gemini Δ fold-in)

<!-- Derived 1:1 from CONCEPT.md (I1 of record). Anything beyond I1 is marked [OPEN]. -->
<!-- Delphi Oracle improvement pass pending: receipts (ABSTAIN/ALLOW/ESCALATE) ⇒ Spec v2. -->
<!-- Gemini Δ folded in 2026-11-01 (v1.1): Δ1 surface correction, features, hybrid persistence. -->

## 1. Problem

Repo history is write-only memory: commits, PRs and file mutations accumulate, but the
*story* — what changed together, what it put at risk, who touched it — must be re-derived by
every reviewer and maintainer, every time.

## 2. Product

A GitHub App that turns a repository's event-stream into a cited narrative:

1. **Ingest** — commits × file mutations × authors (the Gource data plane, ¬ its animation).
2. **Cluster** — group events into story units (by change coupling, file neighborhoods,
   authorship, time windows) [OPEN: clustering signals/thresholds = v2].
3. **Blast radius** — each unit carries its touched-surface/risk footprint.
4. **Narrate** — generate the story with **every claim cited ↦ source commit**; an uncited
   claim does not ship.
5. **Publish** — a GitHub Action posts/updates a **sticky story** on the PR.
6. **Features (Gemini fold-in):** Impact Areas alerts · Automated Changelogs with Receipts ·
   Contextual Blame · blast-radius maintenance warning (file changed without its coupled
   test file ⇒ warning before human review).

## 3. Pipeline (of record)

`git history → PyDriller extraction (Python) → clustering + blast-radius → cited narrative → GitHub Action sticky comment`

Concrete artifacts (Gemini fold-in): scripts `extract_pr_story_context` +
`mine_pr_evolution` (file-coupling matrix; payload {metadata, chronological_stream,
architectural_coupling}); workflow `.github/workflows/pr_storyteller.yml` on
`pull_request: [opened, synchronize]`, posting the story as the sticky first PR comment;
narration driven by the "technical code chronicler" system prompt (verbatim in
`docs/GEMINI-CONCEPT-VERBATIM.md`).

## 4. Persistence [OPEN — I1 candidate set, pick in v2]

- `.story/` JSON in-repo · vector index · SQL chrono-graph. One primary store; the set is
  I1's options, not a commitment to all three.
- Gemini recommendation (fold-in, [OPEN] for v2): **hybrid** — merge → Action → central
  datastore → coupling alerts → pinned Story; M1 `.story/` PR-{id}.json (orphan refs/notes),
  M2 ChromaDB local (`.story_vector_db` / `repo_history_stories`), M3 SQL chrono-graph
  (Commits/FileMutations/Coupling, `shared_commit_count` smell flag).

## 5. Surfaces

- **GitHub Action** `pr_storyteller.yml` (primary, of record per Gemini verbatim Δ1):
  `pull_request [opened, synchronize]` ⇒ sticky first PR comment.
- **Pre-push hook:** lightweight local run ⇒ draft PR description.
- **Pinned markdown Story** on the PR thread.
- ~~GitHub App~~ — I1's label only; the source concept specifies no App (Δ1, CONCEPT.md).
- C8 shape [OPEN]: Forge app surface for Atlassian products — a separate surface decision,
  gated on the C8 entry decision; ∅ claim until then.

## 6. Non-goals

- ≁ Repo Replay (session-provenance .git alternative) — no shared engine/entry, ever.
- ≁ Gource-style animation/visualization for its own sake.
- ∅ uncited narrative claims.

## 7. Build route

Fleet Swarm Desk issue trigger (Swarm-token authored) under manager oversight (chat 8cc20168);
∅ direct lane hand-builds. Website: showcase page, pattern `/delphi-oracle/`, claims ceiling
= this concept of record.
