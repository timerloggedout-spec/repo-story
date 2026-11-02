"""story.config parsing with shipped defaults (SPEC section 3, Delta B/C).

Config is a flat ``key = value`` file. Thresholds live here, never in code,
so per-repo overrides do not fork the engine.
"""
from __future__ import annotations

DEFAULTS = {
    # Blast radius: warn when coupling(a, b) >= tau and b is absent from the PR.
    "blast_tau": "0.5",
    # Clustering time window in hours: commits further apart than this do
    # not join the same story unit on the time signal alone.
    "cluster_window_hours": "24",
    # History window (commits) mined for coupling inside the pr_range scope:
    # commits preceding the range that are available locally. Incremental
    # only -- never a full-history re-mine per PR (SPEC section 8).
    "history_window_commits": "200",
    # Per-PR narration budget (seconds); exceeding it forces the
    # deterministic fallback (SPEC section 6).
    "narrate_budget_seconds": "120",
    # LLM engine: provider key read from this env var when set; absent or
    # failing engine => deterministic fallback, never a hard Action failure.
    "llm_provider": "none",
    "llm_env_key": "REPO_STORY_LLM_API_KEY",
    # Noise filter (pre-cluster): path substrings excluded as story noise.
    "noise_patterns": "lock,.lock,.min.js,.map,__snapshots__,.snap",
    "audit_sample_size": "5",
    "audit_seed": "42",
}


def load_config(text: str | None) -> dict:
    cfg = dict(DEFAULTS)
    if text:
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            cfg[key.strip()] = value.strip()
    cfg["blast_tau"] = float(cfg["blast_tau"])
    cfg["cluster_window_hours"] = float(cfg["cluster_window_hours"])
    cfg["history_window_commits"] = int(cfg["history_window_commits"])
    cfg["narrate_budget_seconds"] = float(cfg["narrate_budget_seconds"])
    cfg["audit_sample_size"] = int(cfg["audit_sample_size"])
    cfg["audit_seed"] = int(cfg["audit_seed"])
    cfg["noise_patterns"] = [p for p in str(cfg["noise_patterns"]).split(",") if p]
    return cfg


def is_noise(path: str, cfg: dict) -> bool:
    return any(pat in path for pat in cfg["noise_patterns"])
