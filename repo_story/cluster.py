"""Cluster events into story units per pinned config (SPEC section 3)."""
from __future__ import annotations

def cluster(commits: list[dict], cfg: dict) -> list[dict]:
    patterns = cfg.get("noise_patterns", [])
    filtered = []
    for c in commits:
        files = [f for f in c["files"] if not any(p in f["path"] for p in patterns)]
        if files:
            c_copy = dict(c)
            c_copy["files"] = files
            filtered.append(c_copy)

    if not filtered:
        return []

    # Simple unit grouping by time window & file neighborhood
    units = []
    current_unit_commits = [filtered[0]]
    current_files = {f["path"] for f in filtered[0]["files"]}
    window = cfg.get("cluster_window_hours", 24) * 3600

    for c in filtered[1:]:
        last_ts = current_unit_commits[-1]["ts"]
        c_files = {f["path"] for f in c["files"]}
        if (c["ts"] - last_ts <= window) or (current_files & c_files):
            current_unit_commits.append(c)
            current_files.update(c_files)
        else:
            units.append({
                "title": f"Story Unit ({current_unit_commits[0]['sha'][:8]})",
                "commits": current_unit_commits,
                "files": sorted(current_files),
            })
            current_unit_commits = [c]
            current_files = c_files

    if current_unit_commits:
        units.append({
            "title": f"Story Unit ({current_unit_commits[0]['sha'][:8]})",
            "commits": current_unit_commits,
            "files": sorted(current_files),
        })

    return units
