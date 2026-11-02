"""Configuration loader for story.config."""
from typing import Any

def load_config(text: str | None = None) -> dict[str, Any]:
    cfg = {
        "blast_tau": 0.5,
        "cluster_window_hours": 24,
        "history_window_commits": 200,
        "narrate_budget_seconds": 120,
        "llm_provider": "none",
        "llm_env_key": "REPO_STORY_LLM_API_KEY",
        "noise_patterns": ["lock", ".lock", ".min.js", ".map", "__snapshots__", ".snap"],
    }
    if not text:
        return cfg
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, v = line.split("=", 1)
            k, v = k.strip(), v.strip()
            if v.replace(".", "", 1).isdigit():
                cfg[k] = float(v) if "." in v else int(v)
            elif k == "noise_patterns":
                cfg[k] = [p.strip() for p in v.split(",")]
            else:
                cfg[k] = v
    return cfg
