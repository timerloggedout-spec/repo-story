"""Pipeline runner: extract -> cluster -> blast -> narrate -> verify ->
publish. Verify is a hard gate: an unverified story never publishes;
a blocked story emits its receipt and exits non-zero (SPEC section 2.5).

Usage:
  python -m repo_story.cli --repo . --base <sha> --head <sha> \
      --pr <number> --repo-slug owner/name --out story.json [--publish]
Publishing needs GITHUB_TOKEN in env (the workflow passes the RepoStory
App installation token).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone

from . import blast as blast_mod
from . import cluster as cluster_mod
from . import narrate as narrate_mod
from . import publish as publish_mod
from . import verify as verify_mod
from .config import load_config
from .extract import extract_range


def run_pipeline(repo: str, base: str, head: str, cfg: dict) -> dict:
    payload = extract_range(repo, base, head, cfg["history_window_commits"])
    units = cluster_mod.cluster(payload["commits"], cfg)
    index = blast_mod.coupling_index(payload["history"])
    warns = blast_mod.warnings(payload["pr_files"], index, cfg)
    narration = narrate_mod.narrate(payload, units, warns, cfg)
    receipt = verify_mod.verify(narration["text"], payload["commits"])
    return {"payload": payload, "units": units, "warnings": warns,
            "narration": narration, "verify": receipt}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--base", required=True)
    ap.add_argument("--head", required=True)
    ap.add_argument("--pr", type=int, required=True)
    ap.add_argument("--repo-slug", required=True)
    ap.add_argument("--config", default="story.config")
    ap.add_argument("--out", default="story.json")
    ap.add_argument("--publish", action="store_true")
    ap.add_argument("--api-base", default="https://api.github.com")
    args = ap.parse_args(argv)

    cfg_text = None
    cfg_path = os.path.join(args.repo, args.config)
    if os.path.exists(cfg_path):
        with open(cfg_path) as f:
            cfg_text = f.read()
    cfg = load_config(cfg_text)

    result = run_pipeline(args.repo, args.base, args.head, cfg)
    header = {
        "pr_number": args.pr,
        "pr_range": result["payload"]["range"],
        "head_sha": result["payload"]["head_sha"],
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    record = publish_mod.story_record(
        result["payload"], result["units"], result["warnings"],
        result["narration"], result["verify"], header)
    with open(args.out, "w") as f:
        json.dump(record, f, indent=1, sort_keys=True)

    if not result["verify"]["ok"]:
        print("VERIFY GATE: story blocked — receipt:", 
              json.dumps(result["verify"]), file=sys.stderr)
        return 2
    if args.publish:
        token = os.environ.get("GITHUB_TOKEN", "")
        body = publish_mod.render_comment(
            result["narration"]["text"], header,
            {"engine": result["narration"]["engine"],
             "version": result["narration"]["version"],
             "mode": result["narration"]["mode"],
             "verify": result["verify"]})
        publish_mod.upsert_sticky(args.api_base, args.repo_slug, args.pr,
                                  body, token)
        print(f"published sticky story on PR {args.pr}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
