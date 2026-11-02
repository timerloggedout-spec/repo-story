"""Extract: a PR's commit range -> commits x file mutations x authors.

Reads a local git checkout (the Action checks out the PR with history).
No full-history mining: the range plus a bounded preceding window only
(SPEC section 8 scale bound).
"""
from __future__ import annotations

import subprocess

_SEP = "\x1f"
_REC = "\x1e"


def _git(args: list[str], cwd: str) -> str:
    out = subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, check=True
    )
    return out.stdout


def extract_range(repo: str, base: str, head: str, history_window: int) -> dict:
    """Return {commits: [...], pr_files: [...], history: [...]}.

    commits: range commits (base..head), oldest first, each
    {sha, author, ts, message, files: [{path, status}]}.
    history: up to ``history_window`` commits preceding the range on the
    base side, same shape minus messages (coupling input only).
    """
    fmt = _REC + _SEP.join(["%H", "%an", "%at", "%s"])
    raw = _git(
        ["log", "--reverse", "--name-status", f"--pretty=format:{fmt}",
         f"{base}..{head}"],
        repo,
    )
    commits = _parse_log(raw)
    hist_raw = _git(
        ["log", f"-{history_window}", "--name-only",
         f"--pretty=format:{fmt}", base],
        repo,
    )
    history = _parse_log(hist_raw, with_status=False)
    pr_files = sorted({f["path"] for c in commits for f in c["files"]})
    return {"commits": commits, "pr_files": pr_files, "history": history,
            "range": f"{base}..{head}", "head_sha": head}


def _parse_log(raw: str, with_status: bool = True) -> list[dict]:
    commits = []
    for record in raw.split(_REC):
        record = record.strip("\n")
        if not record.strip():
            continue
        header, _, body = record.partition("\n")
        parts = header.split(_SEP)
        if len(parts) < 4:
            continue
        sha, author, ts, message = parts[0], parts[1], parts[2], parts[3]
        files = []
        for line in body.splitlines():
            line = line.strip()
            if not line:
                continue
            if with_status:
                bits = line.split("\t")
                if len(bits) >= 2:
                    files.append({"path": bits[-1], "status": bits[0]})
            else:
                files.append({"path": line, "status": ""})
        commits.append({
            "sha": sha, "author": author, "ts": int(ts),
            "message": message, "files": files,
        })
    return commits
