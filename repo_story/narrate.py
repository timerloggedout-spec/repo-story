"""Narrate (SPEC section 6 Delta G).

Engine contract: the "technical code chronicler" system prompt (verbatim
in docs/GEMINI-CONCEPT-VERBATIM.md) over a configurable LLM provider.
v0 ships the deterministic template renderer as the always-available
path: when no LLM provider is configured, the engine errors, or the
per-PR budget is exceeded, the story is template-rendered from the
extraction payload -- the Action never hard-fails a PR for narration.

Every claim the renderer emits is a citation link ``[path](sha)`` whose
commit touches that path, so the verify gate can check 100% of claims.
Rendering is deterministic: same payload + same engine version =>
identical story structure (SPEC section 8 determinism criterion).
"""
from __future__ import annotations

import os
import time

from . import ENGINE_NAME, ENGINE_VERSION

CHRONICLER_PROMPT_REF = "docs/GEMINI-CONCEPT-VERBATIM.md"


def _short(sha: str) -> str:
    return sha[:7]


def render_template(payload: dict, units: list[dict],
                      blast_warnings: list[dict]) -> str:
    """Deterministic story from the extraction payload."""
    lines = []
    commits = {c["sha"]: c for c in payload["commits"]}
    for unit in units:
        lines.append(f"### Story unit {unit['id'] + 1}: "
                     f"{', '.join(unit['neighborhoods'])}")
        for entry in unit["commits"]:
            lines.append(f"- {entry['message']} — {entry['author']}")
            for f in entry["files"]:
                lines.append(
                    f"  - [{f['path']}]({_short(entry['sha'])}) "
                    f"({f['status'] or 'modified'})")
        lines.append("")
    if blast_warnings:
        lines.append("### Impact areas — coupled files absent from this PR")
        by_file = {}
        for w in blast_warnings:
            by_file.setdefault(w["pr_file"], []).append(w)
        for pr_file in sorted(by_file):
            sha = next(
                (c["sha"] for c in payload["commits"]
                 if any(f["path"] == pr_file for f in c["files"])), None)
            if sha is None:
                continue
            absent = ", ".join(
                f"{w['coupled_absent']} (coupling {w['coupling']})"
                for w in by_file[pr_file])
            lines.append(f"- [{pr_file}]({_short(sha)}) changed; "
                         f"historically coupled and absent: {absent}")
        lines.append("")
    if not units:
        lines.append("_No story units: every change in range was noise "
                     "under the shipped filter._")
    _ = commits
    return "\n".join(lines).strip() + "\n"


def narrate(payload: dict, units: list[dict], blast_warnings: list[dict],
            cfg: dict) -> dict:
    """Return {text, engine, version, mode} -- mode is 'llm' or 'fallback'.

    The LLM path is attempted only when a provider is configured AND its
    key is present; any failure or budget overrun falls back. (v0 ships
    the interface + fallback; a live provider adapter lands behind the
    same contract without changing callers.)
    """
    started = time.monotonic()
    provider = str(cfg.get("llm_provider", "none")).lower()
    key_present = bool(os.environ.get(str(cfg.get("llm_env_key", ""))))
    if provider not in ("", "none") and key_present:
        try:
            text = _llm_render(payload, units, blast_warnings, cfg)
            if time.monotonic() - started <= cfg["narrate_budget_seconds"]:
                return {"text": text, "engine": f"{provider}-chronicler",
                        "version": ENGINE_VERSION, "mode": "llm"}
        except Exception:
            pass  # fall through to the deterministic fallback
    return {"text": render_template(payload, units, blast_warnings),
            "engine": ENGINE_NAME, "version": ENGINE_VERSION,
            "mode": "fallback"}


def _llm_render(payload, units, blast_warnings, cfg):  # pragma: no cover
    raise RuntimeError("no LLM adapter configured in v0")
