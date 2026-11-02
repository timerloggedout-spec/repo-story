"""Extract commits, file mutations, and history using git subprocess."""
from __future__ import annotations

import subprocess

_REC = "\x1e"
_SEP = "\x1f"


def _parse_log(raw: str) -> list[dict]:
    commits = []
    for chunk in raw.split(_REC):
        if not chunk.strip():
            continue
        lines = chunk.splitlines()
        header = lines[0].split(_SEP)
        if len(header) < 4:
            continue
        sha, author, ts_str, msg = header[0], header[1], header[2], header[3]
        try:
            ts = int(ts_str)
        except ValueError:
            ts = 0
        files = []
        for line in lines[1:]:
            if not line.strip():
                continue
            parts = line.split("\t", 1)
            if len(parts) == 2:
                status, path = parts[0], parts[1]
                files.append({"path": path, "status": status})
        commits.append({
            "sha": sha,
            "author": author,
            "ts": ts,
            "message": msg,
            "files": files,
        })
    return commits


def extract_range(repo: str, base: str, head: str, history_window: int) -> dict:
    fmt = f"%H{_SEP}%an{_SEP}%at{_SEP}%s"
    cmd = ["git", "-C", repo, "log", f"--format={_REC}{fmt}", "--name-status", f"{base}..{head}"]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    commits = _parse_log(res.stdout)

    hist_cmd = ["git", "-C", repo, "log", f"--format={_REC}{fmt}", "--name-status", f"-n{history_window}", head]
    hist_res = subprocess.run(hist_cmd, capture_output=True, text=True, check=True)
    history = _parse_log(hist_res.stdout)

    pr_files = sorted({f["path"] for c in commits for f in c["files"]})
    head_sha = subprocess.run(["git", "-C", repo, "rev-parse", head], capture_output=True, text=True, check=True).stdout.strip()

    return {
        "range": f"{base}..{head}",
        "head_sha": head_sha,
        "commits": commits,
        "history": history,
        "pr_files": pr_files,
    }
