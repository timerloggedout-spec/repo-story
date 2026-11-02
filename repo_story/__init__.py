"""Repo-Story: turns a PR's event stream into a cited, verified narrative.

Pipeline (SPEC v2.1, pr_range scope): extract -> cluster -> blast radius
-> narrate -> citation-verify (hard gate) -> publish (one sticky comment)
with .story/ persistence on an orphan ref.
"""

ENGINE_NAME = "repo-story"
ENGINE_VERSION = "0.1.0"
