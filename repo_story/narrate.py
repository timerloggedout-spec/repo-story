"""Narration engine & deterministic fallback (SPEC section 6)."""
from __future__ import annotations

def render_template(payload: dict, units: list[dict], blast_warnings: list[dict]) -> str:
    lines = [f"# Repo-Story: {payload['range']}", ""]
    for u in units:
        lines.append(f"## {u['title']}")
        lines.append("")
        for c in u["commits"]:
            sha = c["sha"]
            short = sha[:7]
            msg = c["message"].splitlines()[0]
            lines.append(f"- [{msg}]({sha}) by {c['author']}")
            for f in c["files"]:
                lines.append(f"  - `{f['path']}` ({f['status']})")
        lines.append("")

    if blast_warnings:
        lines.append("## ⚠ Blast Radius Warnings")
        lines.append("")
        for w in blast_warnings:
            lines.append(f"- File `{w['pr_file']}` changed, but coupled file `{w['coupled_absent']}` was absent from PR.")
        lines.append("")

    return "\n".join(lines)


def narrate(payload: dict, units: list[dict], blast_warnings: list[dict], cfg: dict) -> dict:
    text = render_template(payload, units, blast_warnings)
    return {
        "text": text,
        "engine": "deterministic-fallback",
        "version": "v0.1",
        "mode": "fallback",
    }
