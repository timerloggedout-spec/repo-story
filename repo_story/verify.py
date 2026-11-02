"""Citation-verify (SPEC section 2.5 Delta A) -- the hard gate between
narrate and publish.

Every claim in the story is a markdown link ``[text](sha)`` whose text
names a file path. Verification:
  1. resolution -- the cited sha (full or unique prefix) is a commit in
     the extracted range;
  2. claim<->diff support -- the cited commit actually touches the file
     its claim text names.
Receipt {total, resolved, supported, ok}; ok requires 100% on both.
A range rewrite (synchronize) re-runs the whole stage: no carried-over
verdicts.
"""
from __future__ import annotations

import re

_CLAIM = re.compile(r"\[([^\]]+)\]\(([0-9a-f]{7,40})\)")


def find_claims(story_text: str) -> list[dict]:
    return [{"text": m.group(1), "sha": m.group(2)}
            for m in _CLAIM.finditer(story_text)]


def verify(story_text: str, commits: list[dict]) -> dict:
    by_sha = {c["sha"]: c for c in commits}
    claims = find_claims(story_text)
    resolved = 0
    supported = 0
    failures = []
    for claim in claims:
        target = None
        if claim["sha"] in by_sha:
            target = by_sha[claim["sha"]]
        else:
            matches = [s for s in by_sha if s.startswith(claim["sha"])]
            if len(matches) == 1:
                target = by_sha[matches[0]]
        if target is None:
            failures.append({"claim": claim, "reason": "unresolved citation"})
            continue
        resolved += 1
        touched = {f["path"] for f in target["files"]}
        named = [p for p in touched if p in claim["text"]]
        if named:
            supported += 1
        else:
            failures.append({"claim": claim,
                             "reason": "cited commit does not touch the named file"})
    total = len(claims)
    return {
        "total": total, "resolved": resolved, "supported": supported,
        "ok": total > 0 and resolved == total and supported == total,
        "failures": failures,
    }
