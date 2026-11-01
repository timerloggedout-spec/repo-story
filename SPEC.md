# Repo+Story — Spec v1 (seed)

<!-- Derived 1:1 from CONCEPT.md (I1 of record). Anything beyond I1 is marked [OPEN]. -->
<!-- Delphi Oracle improvement pass pending: receipts (ABSTAIN/ALLOW/ESCALATE) ⇒ Spec v2. -->
<!-- Gemini Δ fold-in pending: enrichment, ¬ gate. -->

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

## 3. Pipeline (of record)

`git history → PyDriller extraction (Python) → clustering + blast-radius → cited narrative → GitHub Action sticky comment`

## 4. Persistence [OPEN — I1 candidate set, pick in v2]

- `.story/` JSON in-repo · vector index · SQL chrono-graph. One primary store; the set is
  I1's options, not a commitment to all three.

## 5. Surfaces

- GitHub App (primary, of record).
- PR sticky story (output surface, of record).
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
