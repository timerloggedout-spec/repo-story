"""Labeled-set evaluation runner for citation verification (SPEC section 8).

Loads fixture cases from tests/fixtures/labeled/, runs verify.verify(),
computes precision, recall, accuracy, and F1 score against expected ground truth,
and prints the metrics.
"""
from __future__ import annotations

import json
import glob
import os
import unittest

from repo_story import verify


def run_evaluation() -> dict:
    fixture_dir = os.path.join(os.path.dirname(__file__), "fixtures", "labeled")
    pattern = os.path.join(fixture_dir, "*.json")
    case_paths = sorted(glob.glob(pattern))

    tp = 0
    fp = 0
    tn = 0
    fn = 0
    results = []

    for path in case_paths:
        with open(path) as f:
            case = json.load(f)
        actual = verify.verify(case["story_text"], case["commits"])
        expected_ok = case["expected"]["ok"]
        actual_ok = actual["ok"]

        if expected_ok and actual_ok:
            tp += 1
        elif not expected_ok and actual_ok:
            fp += 1
        elif not expected_ok and not actual_ok:
            tn += 1
        elif expected_ok and not actual_ok:
            fn += 1

        results.append({
            "id": case["id"],
            "category": case["category"],
            "expected_ok": expected_ok,
            "actual_ok": actual_ok,
            "match": expected_ok == actual_ok,
        })

    total = len(case_paths)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 1.0
    accuracy = (tp + tn) / total if total > 0 else 1.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    metrics = {
        "total": total,
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "precision": precision,
        "recall": recall,
        "accuracy": accuracy,
        "f1": f1,
        "results": results,
    }
    return metrics


class TestLabeledEval(unittest.TestCase):
    def test_labeled_set_metrics(self):
        metrics = run_evaluation()
        print("\n--- Labeled-Set Citation Verification Evaluation ---")
        print(f"Total fixtures evaluated: {metrics['total']}")
        print(f"TP: {metrics['tp']}, FP: {metrics['fp']}, TN: {metrics['tn']}, FN: {metrics['fn']}")
        print(f"Precision: {metrics['precision']:.3f}")
        print(f"Recall:    {metrics['recall']:.3f}")
        print(f"Accuracy:  {metrics['accuracy']:.3f}")
        print(f"F1 Score:  {metrics['f1']:.3f}")
        print("---------------------------------------------------")
        for r in metrics["results"]:
            status = "PASS" if r["match"] else "FAIL"
            print(f"  [{status}] Case #{r['id']} ({r['category']}): expected {r['expected_ok']}, got {r['actual_ok']}")
        
        self.assertEqual(metrics["precision"], 1.0, "Precision must be 1.0")
        self.assertEqual(metrics["recall"], 1.0, "Recall must be 1.0")
        self.assertEqual(metrics["accuracy"], 1.0, "Accuracy must be 1.0")


if __name__ == "__main__":
    metrics = run_evaluation()
    print("Evaluation Results:", json.dumps(metrics, indent=2))
    if metrics["precision"] == 1.0 and metrics["recall"] == 1.0:
        print("SUCCESS: 100% precision and recall on labeled fixture set.")
    else:
        print("FAILURE: Imperfect evaluation metrics.")
        exit(1)
