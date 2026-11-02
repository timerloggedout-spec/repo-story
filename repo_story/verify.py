"""Citation verification hard gate (SPEC section 2.5 & 8)."""
from __future__ import annotations

import re

def verify(story_text: str, commits: list[dict]) -> dict:
    commit_shas = {c["sha"] for c in commits}
    commit_files = {c["sha"]: {f["path"] for f in c["files"]} for c in commits}

    pattern = re.compile(r'\[([^\]]+)\]\(([a-fA-F0-9]{40})\)')
    matches = pattern.findall(story_text)

    total = len(matches)
    resolved = 0
    supported = 0

    for desc, sha in matches:
        resolved += 1
        if sha in commit_shas:
            supported += 1

    ok = (total > 0 and resolved == total and supported == total) or (total == 0 and len(commits) == 0)

    return {
        "total": total,
        "resolved": resolved,
        "supported": supported,
        "ok": ok,
    }
