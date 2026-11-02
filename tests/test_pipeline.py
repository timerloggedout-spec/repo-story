"""Acceptance tests (SPEC section 8) on a fixture range.

Covers: citation resolution = 100% hard gate, determinism of story
structure, deterministic fallback path, cluster v0 rule, blast-radius
warnings, noise filter.
"""
import unittest

from repo_story import blast, cluster, narrate, verify
from repo_story.config import load_config
from repo_story.extract import _REC, _SEP, _parse_log

CFG = load_config(None)


def commit(sha, author, ts, message, files):
    return {"sha": sha, "author": author, "ts": ts, "message": message,
            "files": [{"path": p, "status": "M"} for p in files]}


FIXTURE_COMMITS = [
    commit("a" * 40, "Ana", 1_700_000_000, "add auth module",
           ["src/auth/login.py", "src/auth/session.py"]),
    commit("b" * 40, "Bo", 1_700_003_600, "wire login route",
           ["src/auth/routes.py", "src/web/app.py"]),
    commit("c" * 40, "Ana", 1_700_200_000, "bump lockfile",
           ["package-lock.json"]),
]

HISTORY = [
    commit("d" * 40, "Ana", 1_699_000_000, "earlier",
           ["src/auth/login.py", "src/auth/tokens.py"]),
    commit("e" * 40, "Bo", 1_699_100_000, "earlier 2",
           ["src/auth/login.py", "src/auth/tokens.py"]),
    commit("f" * 40, "Bo", 1_699_200_000, "unrelated",
           ["docs/readme.md"]),
]


def payload():
    return {"commits": FIXTURE_COMMITS,
            "pr_files": sorted({f["path"] for c in FIXTURE_COMMITS
                                for f in c["files"]}),
            "history": HISTORY, "range": "base..head", "head_sha": "b" * 40}


class TestPipeline(unittest.TestCase):
    def test_cluster_v0_rule_and_noise(self):
        units = cluster.cluster(FIXTURE_COMMITS, CFG)
        # The lockfile-only commit is noise -> excluded pre-cluster.
        self.assertEqual(len(units), 1)
        self.assertEqual(len(units[0]["commits"]), 2)
        self.assertIn("src/auth/login.py", units[0]["files"])

    def test_blast_warning(self):
        idx = blast.coupling_index(HISTORY)
        warns = blast.warnings(payload()["pr_files"], idx, CFG)
        pairs = {(w["pr_file"], w["coupled_absent"]) for w in warns}
        self.assertIn(("src/auth/login.py", "src/auth/tokens.py"), pairs)

    def test_fallback_story_verifies_100(self):
        p = payload()
        units = cluster.cluster(p["commits"], CFG)
        idx = blast.coupling_index(p["history"])
        warns = blast.warnings(p["pr_files"], idx, CFG)
        out = narrate.narrate(p, units, warns, CFG)
        self.assertEqual(out["mode"], "fallback")
        receipt = verify.verify(out["text"], p["commits"])
        self.assertEqual(receipt["resolved"], receipt["total"])
        self.assertEqual(receipt["supported"], receipt["total"])
        self.assertTrue(receipt["ok"])

    def test_determinism(self):
        p = payload()
        units = cluster.cluster(p["commits"], CFG)
        idx = blast.coupling_index(p["history"])
        warns = blast.warnings(p["pr_files"], idx, CFG)
        a = narrate.render_template(p, units, warns)
        b = narrate.render_template(p, units, warns)
        self.assertEqual(a, b)
        ra, rb = verify.verify(a, p["commits"]), verify.verify(b, p["commits"])
        self.assertEqual(ra, rb)

    def test_verify_gate_blocks_bad_citation(self):
        bad = "Claim: [src/auth/login.py](0000000) did things.\n"
        receipt = verify.verify(bad, FIXTURE_COMMITS)
        self.assertFalse(receipt["ok"])
        wrong_file = "Claim: [docs/readme.md](aaaaaaa) did things.\n"
        receipt2 = verify.verify(wrong_file, FIXTURE_COMMITS)
        self.assertFalse(receipt2["ok"])
        self.assertEqual(receipt2["resolved"], 1)
        self.assertEqual(receipt2["supported"], 0)

    def test_extract_parse_log_shape(self):
        # Real git output: record sep leads each commit's header, whose
        # file lines follow within the same chunk.
        raw = (_REC + "a" * 40 + _SEP + "Ana" + _SEP + "1700000000" + _SEP
               + "add auth" + "\nM\tsrc/auth/login.py\nA\tsrc/auth/session.py\n"
               + _REC + "b" * 40 + _SEP + "Bo" + _SEP + "1700003600" + _SEP
               + "wire route" + "\nM\tsrc/web/app.py\n")
        commits = _parse_log(raw)
        self.assertEqual(len(commits), 2)
        self.assertEqual(commits[0]["files"][0],
                         {"path": "src/auth/login.py", "status": "M"})
        self.assertEqual(commits[1]["author"], "Bo")

    def test_sampled_audit_success(self):
        story = (
            f"Changed [src/auth/login.py]({'a'*40}) and "
            f"[src/auth/session.py]({'a'*40}) and "
            f"[src/auth/routes.py]({'b'*40})."
        )
        res = verify.audit(story, FIXTURE_COMMITS, repo=".", cfg=CFG)
        self.assertTrue(res["ok"])
        self.assertGreaterEqual(res["sampled"], 1)
        self.assertEqual(res["sampled"], res["supported"])

    def test_sampled_audit_flags_unsupported_claim(self):
        story = f"Changed [docs/readme.md]({'a'*40})."
        res = verify.audit(story, FIXTURE_COMMITS, repo=".", cfg=CFG)
        self.assertFalse(res["ok"])
        self.assertEqual(res["supported"], 0)

    def test_audit_runs_against_pr4_story_artifact(self):
        pr4_story = "### Unit 1\n- [repo_story/__init__.py](4cb7362) (A)\n"
        pr4_commits = [{
            "sha": "4cb73622ccb05af9e721f4652fc44bb07b0d6fab",
            "author": "bot",
            "ts": 1793613458,
            "message": "init",
            "files": [{"path": "repo_story/__init__.py", "status": "A"}]
        }]
        res = verify.audit(pr4_story, pr4_commits, repo=".", cfg=CFG)
        self.assertTrue(res["ok"])
        self.assertGreaterEqual(res["sampled"], 1)


if __name__ == "__main__":
    unittest.main()
