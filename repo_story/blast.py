"""Blast radius (SPEC section 3 Delta C): co-change graph only.

coupling(a, b) = shared_commit_count(a, b) / max_commits_touching_either,
over the available history window. A warning fires when a file coupled
to a PR file at >= tau is absent from the PR's file set. No
external-dependency inference.
"""
from __future__ import annotations

from itertools import combinations


def coupling_index(history: list[dict]) -> dict:
    """Return {(a, b): coupling} with a < b, plus per-file touch counts."""
    touches: dict[str, int] = {}
    shared: dict[tuple, int] = {}
    for commit in history:
        paths = sorted({f["path"] for f in commit["files"]})
        for p in paths:
            touches[p] = touches.get(p, 0) + 1
        for a, b in combinations(paths, 2):
            shared[(a, b)] = shared.get((a, b), 0) + 1
    coupling = {}
    for (a, b), n in shared.items():
        denom = max(touches.get(a, 0), touches.get(b, 0))
        if denom:
            coupling[(a, b)] = n / denom
    return {"coupling": coupling, "touches": touches}


def warnings(pr_files: list[str], index: dict, cfg: dict) -> list[dict]:
    """Coupled-but-absent warnings for the PR file set, sorted (deterministic)."""
    tau = cfg["blast_tau"]
    present = set(pr_files)
    out = []
    for (a, b), score in sorted(index["coupling"].items()):
        if score < tau:
            continue
        if a in present and b not in present:
            out.append({"pr_file": a, "coupled_absent": b, "coupling": round(score, 3)})
        elif b in present and a not in present:
            out.append({"pr_file": b, "coupled_absent": a, "coupling": round(score, 3)})
    return out
