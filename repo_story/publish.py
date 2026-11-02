"""Publish (SPEC section 5 Delta D + section 7 Delta E v0/M1).

Exactly one sticky comment per PR, edited in place, keyed by a hidden
marker. The comment carries a version header {pr_range, head_sha,
generated_at} and the story self-receipt {input range, engine + version,
citation-verify result} (Delta I). Persistence payload: .story/PR-{id}.json
for the orphan ref (written by the workflow from cli output).
"""
from __future__ import annotations

import json
import urllib.request

MARKER = "<!-- repo-story:sticky -->"


def render_comment(story_text: str, header: dict, receipt: dict) -> str:
    body = [
        MARKER,
        f"## Repo-Story — PR {header['pr_number']}",
        "",
        f"range `{header['pr_range']}` · head `{header['head_sha']}` · "
        f"generated {header['generated_at']}",
        "",
        story_text.rstrip(),
        "",
        "---",
        f"self-receipt: engine {receipt['engine']} {receipt['version']} "
        f"({receipt['mode']}) · citations {receipt['verify']['resolved']}/"
        f"{receipt['verify']['total']} resolved, "
        f"{receipt['verify']['supported']}/{receipt['verify']['total']} "
        f"supported · verify ok: {receipt['verify']['ok']}",
    ]
    return "\n".join(body) + "\n"


def upsert_sticky(api_base: str, repo: str, pr_number: int, body: str,
                  token: str) -> dict:
    """Create or edit-in-place the one sticky comment. Returns the comment."""
    def req(method, url, data=None):
        r = urllib.request.Request(
            url,
            data=json.dumps(data).encode() if data is not None else None,
            headers={"Authorization": f"Bearer {token}",
                     "Accept": "application/vnd.github+json",
                     "Content-Type": "application/json"},
            method=method)
        with urllib.request.urlopen(r) as resp:
            return json.loads(resp.read().decode())

    comments = req("GET", f"{api_base}/repos/{repo}/issues/{pr_number}"
                          f"/comments?per_page=100")
    for c in comments:
        if MARKER in (c.get("body") or ""):
            return req("PATCH", f"{api_base}/repos/{repo}/issues/comments/"
                                f"{c['id']}", {"body": body})
    return req("POST", f"{api_base}/repos/{repo}/issues/{pr_number}/comments",
               {"body": body})


def story_record(payload: dict, units: list[dict], blast_warnings: list[dict],
                 narration: dict, receipt_verify: dict, header: dict) -> dict:
    """The .story/PR-{id}.json persistence record (M1)."""
    return {
        "schema": "repo-story/v0",
        "header": header,
        "units": units,
        "blast_warnings": blast_warnings,
        "story": narration["text"],
        "engine": {"name": narration["engine"],
                   "version": narration["version"], "mode": narration["mode"]},
        "verify": receipt_verify,
        "pr_files": payload["pr_files"],
    }
