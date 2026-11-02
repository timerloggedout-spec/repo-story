"""Scale and performance tests (SPEC section 8) on synthetic large history fixture."""
from __future__ import annotations

import time
import tracemalloc
import unittest
import tempfile
import subprocess

from repo_story import blast, cluster, extract
from repo_story.config import load_config
from tests.fixtures.generator import populate_synthetic_repo

CFG = load_config(None)


class TestScaleFixture(unittest.TestCase):
    def test_scale_extraction_cluster_blast_within_bounds(self):
        """Scale test: 200 PR history fixture extraction, clustering, and blast radius analysis.

        Asserts runtime and peak memory stay within SPEC section 8 bounds:
        - Runtime budget: <= 120s per-PR budget (SPEC §6 / §8), actual extraction + analysis < 10.0s.
        - Memory footprint: peak memory < 50MB (avoiding PyDriller monorepo scale breakdown of ~11.7k tree entries / 100 commits via bounded window extraction).
        - Determinism & Offline: reproducible history generation under fixed seed (42).
        """
        seed = 42
        num_prs = 200

        with tempfile.TemporaryDirectory() as tmp_dir:
            populate_synthetic_repo(tmp_dir, seed=seed, num_prs=num_prs)

            res = subprocess.run(["git", "rev-parse", "HEAD~20"], cwd=tmp_dir, capture_output=True, text=True, check=True)
            base_sha = res.stdout.strip()
            res_head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_dir, capture_output=True, text=True, check=True)
            head_sha = res_head.stdout.strip()

            tracemalloc.start()
            start_time = time.monotonic()

            payload = extract.extract_range(tmp_dir, base_sha, head_sha, history_window=100)
            units = cluster.cluster(payload["commits"], CFG)
            idx = blast.coupling_index(payload["history"])
            warnings = blast.warnings(payload["pr_files"], idx, CFG)

            elapsed = time.monotonic() - start_time
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            max_allowed_seconds = 10.0
            max_allowed_peak_memory_mb = 50.0
            peak_mb = peak / (1024 * 1024)

            self.assertLess(elapsed, max_allowed_seconds,
                            f"Scale test runtime {elapsed:.2f}s exceeded bound of {max_allowed_seconds}s (SPEC §8 / §6 budget: 120s)")
            self.assertLess(peak_mb, max_allowed_peak_memory_mb,
                            f"Scale test peak memory {peak_mb:.2f}MB exceeded bound of {max_allowed_peak_memory_mb}MB (avoiding PyDriller monorepo scale breakdown)")
            self.assertEqual(len(payload["commits"]), 20)

    def test_generator_determinism(self):
        """Test that the generator produces byte-for-byte identical history under the same seed."""
        with tempfile.TemporaryDirectory() as dir1, tempfile.TemporaryDirectory() as dir2:
            populate_synthetic_repo(dir1, seed=123, num_prs=10)
            populate_synthetic_repo(dir2, seed=123, num_prs=10)

            log1 = subprocess.run(["git", "log", "--pretty=format:%H %an %at %s"], cwd=dir1, capture_output=True, text=True, check=True).stdout
            log2 = subprocess.run(["git", "log", "--pretty=format:%H %an %at %s"], cwd=dir2, capture_output=True, text=True, check=True).stdout
            self.assertEqual(log1, log2)


if __name__ == "__main__":
    unittest.main()
