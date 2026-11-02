"""Cluster (v0 rule, SPEC section 3 Delta B): same-PR + file neighborhood
+ time window. Noise is filtered pre-cluster. Coupling/authorship signals
phase in with the labeled-set eval (section 8) -- not in v0.
"""
from __future__ import annotations

from .config import is_noise


def _neighborhood(path: str) -> str:
    """File neighborhood = the path's directory (top two components)."""
    parts = path.split("/")
    return "/".join(parts[:2]) if len(parts) > 2 else (parts[0] if parts else "")


def cluster(commits: list[dict], cfg: dict) -> list[dict]:
    """Group range commits into story units.

    Two commits join one unit when they share a file neighborhood and
    fall within the configured time window of the unit's latest commit.
    Units are returned in first-appearance order (deterministic).
    """
    window = cfg["cluster_window_hours"] * 3600
    units: list[dict] = []
    for commit in commits:
        files = [f for f in commit["files"] if not is_noise(f["path"], cfg)]
        if not files:
            continue
        hoods = {_neighborhood(f["path"]) for f in files}
        placed = None
        for unit in units:
            if hoods & unit["neighborhoods"] and (
                commit["ts"] - unit["last_ts"] <= window
            ):
                placed = unit
                break
        entry = {"sha": commit["sha"], "author": commit["author"],
                 "ts": commit["ts"], "message": commit["message"],
                 "files": files}
        if placed is None:
            units.append({
                "id": len(units),
                "neighborhoods": set(hoods),
                "commits": [entry],
                "last_ts": commit["ts"],
            })
        else:
            placed["commits"].append(entry)
            placed["neighborhoods"] |= hoods
            placed["last_ts"] = max(placed["last_ts"], commit["ts"])
    for unit in units:
        unit["neighborhoods"] = sorted(unit["neighborhoods"])
        unit["files"] = sorted(
            {f["path"] for c in unit["commits"] for f in c["files"]})
        unit["authors"] = sorted({c["author"] for c in unit["commits"]})
    return units
