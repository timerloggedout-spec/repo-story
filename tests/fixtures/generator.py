"""Deterministic synthetic git history generator for scale tests (SPEC section 8)."""
from __future__ import annotations

import os
import random
import subprocess
from pathlib import Path


def populate_synthetic_repo(repo_path: str, seed: int = 42, num_prs: int = 200) -> None:
    """Populate an existing directory with a git repo containing ~num_prs commits/PRs deterministically.

    Offline, seeded, reproducible byte-for-byte under the same seed.
    """
    rng = random.Random(seed)

    subprocess.run(["git", "init", "-b", "main"], cwd=repo_path, capture_output=True, check=True)
    subprocess.run(["git", "config", "user.name", "Synthetic Author"], cwd=repo_path, capture_output=True, check=True)
    subprocess.run(["git", "config", "user.email", "author@example.com"], cwd=repo_path, capture_output=True, check=True)

    authors = ["Ana", "Bo", "Chan", "Di", "Eva"]
    modules = ["auth", "web", "api", "db", "storage", "billing", "ui", "util"]

    base_time = 1_700_000_000

    for i in range(num_prs):
        author = rng.choice(authors)
        base_time += rng.randint(1800, 10800)

        num_files = rng.randint(1, 4)
        files_to_touch = set()
        for _ in range(num_files):
            mod = rng.choice(modules)
            filename = f"src/{mod}/{rng.choice(['core.py', 'models.py', 'routes.py', 'utils.py'])}"
            files_to_touch.add(filename)

        if rng.random() < 0.2:
            files_to_touch.add("package-lock.json")
        if rng.random() < 0.3:
            files_to_touch.add(f"docs/feature-{i}.md")

        for fpath in files_to_touch:
            full_path = Path(repo_path) / fpath
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, "a", encoding="utf-8") as f:
                f.write(f"# Commit {i} by {author} for {fpath}\n")

        subprocess.run(["git", "add", "."], cwd=repo_path, capture_output=True, check=True)
        env = os.environ.copy()
        env["GIT_AUTHOR_DATE"] = str(base_time)
        env["GIT_COMMITTER_DATE"] = str(base_time)
        env["GIT_AUTHOR_NAME"] = author
        env["GIT_COMMITTER_NAME"] = author
        msg = f"feat: synthetic PR #{i+1} update module components"
        subprocess.run(
            ["git", "commit", "-m", msg, "--no-gpg-sign"],
            cwd=repo_path, env=env, capture_output=True, check=True
        )
