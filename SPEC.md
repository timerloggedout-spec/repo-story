# Repo+Story — Spec v2 (oracle-folded)

<!-- v2 = v1.2 + Delphi Oracle pass fold (evaluator: D0 seat 7f59b235, kernel deterministic_oracle -->
<!-- @delphi-oracle 393e1f4b; receipts in docs/ORACLE-PASS.md). Builder≠evaluator held. -->
<!-- Receipts: ALLOW ×2 (R1 core pipeline · R2 Δ1 fold) · ABSTAIN ×8 (R3–R10) ⇒ ΔA–ΔI below · -->
<!-- ESCALATE ×1 (R11 C8/Forge — gate held, §9). Refinements from Delphi draft list folded: -->
<!-- co-change-only blast · rewrite⇒re-verify · scale test · determinism · ΔE hybrid-target. -->

## 1. Problem

Repo history is write-only memory: commits, PRs and file mutations accumulate, but the
*story* — what changed together, what it put at risk, who touched it — must be re-derived by
every reviewer and maintainer, every time.

## 2. Product

A GitHub Action + pre-push hook system that turns a repository's event-stream into a cited
narrative:

1. **Ingest** — commits × file mutations × authors (the Gource data plane, ¬ its animation).
2. **Cluster** — group events into story units per the pinned config in §3 (ΔB).
3. **Blast radius** — each unit carries its risk footprint per the metric in §3 (ΔC).
4. **Narrate** — generate the story with **every claim cited ↦ source commit**.
5. **Verify** (ΔA) — citation-verify stage between narrate and publish: resolve every
   `[Desc](commit_hash)` and check claim↔diff support. Fail ⇒ story blocked + receipt
   emitted; an unverified story never publishes. Any rewrite of the range (synchronize)
   ⇒ full re-verify (no carried-over verdicts).
6. **Publish** — a GitHub Action posts/updates the **sticky story** on the PR (§5 semantics).
7. **Features:** Impact Areas alerts · Automated Changelogs with Receipts · Contextual
   Blame · blast-radius maintenance warning (coupled file absent from the PR ⇒ warning
   before human review).

## 3. Clustering + blast radius (ΔB, ΔC)

- **Clustering signals (pinned):** co-change coupling · file neighborhood · authorship ·
  time window. Noise filter: lockfiles, linters, formatters excluded pre-cluster.
  Thresholds live in repo config (`story.config`) with shipped defaults — [OPEN: default
  values tuned on the labeled PR set, §8].
- **Blast-radius metric:** coupling(a,b) = shared_commit_count over the history window,
  normalized; warning ⇔ a coupled file (coupling ≥ τ) is absent from the PR's file set.
  τ = shipped default + per-repo override. **Co-change graph only — no external-dependency
  inference** (Delphi refinement).

## 4. Scopes (ΔF)

Two named scopes, never conflated:
- `pr_range` — the PR's commit range; drives the narrative.
- `history_index` — whole-history coupling mining; refreshed on merge, feeds §3.

## 5. Publish semantics (ΔD)

- Exactly **one** sticky comment per PR, edited in place.
- Version header on every story: {pr_range, head_sha, generated_at}.
- Superseded ranges are folded/collapsed, never stacked as new comments.
- **Story self-receipt (ΔI):** the comment carries {input range, engine + version,
  citation-verify result} — evidence-over-claims applied to the story itself.

## 6. Narration engine (ΔG)

- Engine contract: the "technical code chronicler" system prompt (verbatim in
  `docs/GEMINI-CONCEPT-VERBATIM.md`) over a configurable LLM provider; engine name +
  version stamped into the self-receipt (§5).
- **Deterministic fallback:** if the engine is unavailable or the per-PR cost/latency
  budget (config) is exceeded, publish a template-rendered story from the extraction
  payload — the Action never hard-fails a PR for narration.
- Acceptance includes a **determinism criterion**: same input range + same engine
  version ⇒ same verified story structure (citations + clusters identical).

## 7. Persistence (ΔE, as amended)

- **v0 (sequencing):** M1 — `.story/` PR-{id}.json on an orphan ref (git-native, ∅ infra).
- **Target architecture:** the source-recommended **hybrid** — merge → Action → central
  datastore → coupling alerts → pinned Story; M2 ChromaDB local vector
  (`.story_vector_db` / `repo_history_stories`) and M3 SQL chrono-graph
  (Commits/FileMutations/Coupling, `shared_commit_count` smell flag) land when the
  `history_index` scope ships (trigger: coupling alerts enabled).

## 8. Acceptance criteria (ΔH + refinements)

- Citation resolution = **100% hard gate** (§2.5 verify stage receipts).
- Claim-support: sampled audit of published stories, support rate reported per release.
- Cluster quality: evaluated on a labeled PR set; precision/recall recorded, not asserted.
- Runtime budget: Action completes within the configured per-PR budget (§6) or falls back.
- **Scale test:** extraction + verify run on a large-history repo fixture within budget.
- **Determinism:** §6 criterion demonstrated on the labeled set.

## 9. Competition surface — GATED (R11 ESCALATE, held)

C8 Codegeist 2026 mapping stands (candidate only). The Forge/Atlassian surface is an
**entry decision for manager/owner**, not a build item: ∅ Forge work, ∅ claim language
until an entry decision is recorded. C9/C10 remain △ alternates.

## 10. Non-goals

- ≁ Repo Replay (session-provenance .git alternative) — no shared engine/entry, ever.
- ≁ Gource-style animation/visualization for its own sake.
- ∅ uncited narrative claims; ∅ unverified stories (§2.5).
