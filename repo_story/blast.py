"""Blast-radius coupling metric (SPEC section 3 & Delta C)."""
from __future__ import annotations

def coupling_index(history: list[dict]) -> dict[tuple[str, str], int]:
    co_changes = {}
    for c in history:
        paths = sorted({f["path"] for f in c["files"]})
        for i in range(len(paths)):
            for j in range(i + 1, len(paths)):
                pair = (paths[i], paths[j])
                co_changes[pair] = co_changes.get(pair, 0) + 1
    return co_changes


def warnings(pr_files: list[str], coupling: dict[tuple[str, str], int], cfg: dict) -> list[dict]:
    tau = cfg.get("blast_tau", 0.5)
    warns = []
    pr_set = set(pr_files)
    for (a, b), count in coupling.items():
        if count >= max(1, int(tau * 2)):
            if a in pr_set and b not in pr_set:
                warns.append({"pr_file": a, "coupled_absent": b, "shared_count": count})
            elif b in pr_set and a not in pr_set:
                warns.append({"pr_file": b, "coupled_absent": a, "shared_count": count})
    return warns
