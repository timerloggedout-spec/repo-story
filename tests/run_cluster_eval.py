"""Labeled-set evaluation runner for cluster quality (SPEC section 8).

Loads fixture cases from tests/fixtures/cluster/*.json, runs cluster.cluster(),
and computes precision, recall, accuracy, and F1 score of commit-pair co-membership
between predicted cluster units and ground-truth story-unit assignments.

Pair co-membership definition:
For all pairs of commits (c_i, c_j) with i < j across evaluated commits in the fixture:
- TP (True Positive): pair is in the same unit in both ground-truth and prediction.
- FP (False Positive): pair is in the same unit in prediction, but different units in ground-truth.
- TN (True Negative): pair is in different units in both ground-truth and prediction.
- FN (False Negative): pair is in the same unit in ground-truth, but different units in prediction.
"""
from __future__ import annotations

import json
import glob
import os

from repo_story import cluster
from repo_story.config import load_config


def run_evaluation() -> dict:
    fixture_dir = os.path.join(os.path.dirname(__file__), "fixtures", "cluster")
    pattern = os.path.join(fixture_dir, "*.json")
    case_paths = sorted(glob.glob(pattern))

    total_tp = 0
    total_fp = 0
    total_tn = 0
    total_fn = 0
    results = []

    for path in case_paths:
        with open(path) as f:
            case = json.load(f)

        cfg = load_config(None)
        if "config" in case:
            cfg.update(case["config"])

        commits = case["commits"]
        expected_units = case["expected_units"]

        predicted_units = cluster.cluster(commits, cfg)
        predicted_shas_list = [[c["sha"] for c in u["commits"]] for u in predicted_units]

        # Build ground-truth mapping: sha -> unit_index
        gt_map = {}
        for idx, u_shas in enumerate(expected_units):
            for sha in u_shas:
                gt_map[sha] = idx

        # Build predicted mapping: sha -> unit_index
        pred_map = {}
        for idx, u_shas in enumerate(predicted_shas_list):
            for sha in u_shas:
                pred_map[sha] = idx

        evaluated_shas = sorted(list(gt_map.keys()))

        case_tp = 0
        case_fp = 0
        case_tn = 0
        case_fn = 0

        n = len(evaluated_shas)
        for i in range(n):
            for j in range(i + 1, n):
                sha_i = evaluated_shas[i]
                sha_j = evaluated_shas[j]

                gt_same = gt_map.get(sha_i) == gt_map.get(sha_j)
                pred_same = pred_map.get(sha_i) == pred_map.get(sha_j)

                if gt_same and pred_same:
                    case_tp += 1
                elif not gt_same and pred_same:
                    case_fp += 1
                elif not gt_same and not pred_same:
                    case_tn += 1
                elif gt_same and not pred_same:
                    case_fn += 1

        total_tp += case_tp
        total_fp += case_fp
        total_tn += case_tn
        total_fn += case_fn

        case_total_pairs = case_tp + case_fp + case_tn + case_fn
        case_precision = case_tp / (case_tp + case_fp) if (case_tp + case_fp) > 0 else 1.0
        case_recall = case_tp / (case_tp + case_fn) if (case_tp + case_fn) > 0 else 1.0

        results.append({
            "id": case["id"],
            "category": case["category"],
            "tp": case_tp,
            "fp": case_fp,
            "tn": case_tn,
            "fn": case_fn,
            "precision": case_precision,
            "recall": case_recall,
            "match": case_fp == 0 and case_fn == 0,
        })

    total_pairs = total_tp + total_fp + total_tn + total_fn
    precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 1.0
    recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 1.0
    accuracy = (total_tp + total_tn) / total_pairs if total_pairs > 0 else 1.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    metrics = {
        "total_fixtures": len(case_paths),
        "total_pairs": total_pairs,
        "tp": total_tp,
        "fp": total_fp,
        "tn": total_tn,
        "fn": total_fn,
        "precision": precision,
        "recall": recall,
        "accuracy": accuracy,
        "f1": f1,
        "results": results,
    }
    return metrics


if __name__ == "__main__":
    metrics = run_evaluation()
    print("Cluster Evaluation Results:", json.dumps(metrics, indent=2))
    if metrics["precision"] == 1.0 and metrics["recall"] == 1.0:
        print("SUCCESS: 100% precision and recall on cluster fixture set.")
    else:
        print("FAILURE: Imperfect cluster evaluation metrics.")
        exit(1)
