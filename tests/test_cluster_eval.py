"""Unit test wrapper for cluster quality precision/recall evaluation."""
import unittest
from tests.run_cluster_eval import run_evaluation


class TestClusterEval(unittest.TestCase):
    def test_cluster_precision_recall_100_percent(self):
        metrics = run_evaluation()
        print("\n--- Cluster Quality Precision & Recall Evaluation ---")
        print(f"Total fixtures evaluated: {metrics['total_fixtures']}")
        print(f"Total commit pairs: {metrics['total_pairs']}")
        print(f"TP: {metrics['tp']}, FP: {metrics['fp']}, TN: {metrics['tn']}, FN: {metrics['fn']}")
        print(f"Precision: {metrics['precision']:.3f}")
        print(f"Recall:    {metrics['recall']:.3f}")
        print(f"Accuracy:  {metrics['accuracy']:.3f}")
        print(f"F1 Score:  {metrics['f1']:.3f}")
        print("-----------------------------------------------------")
        for r in metrics["results"]:
            status = "PASS" if r["match"] else "FAIL"
            print(f"  [{status}] Case #{r['id']} ({r['category']}): precision={r['precision']:.3f}, recall={r['recall']:.3f}")

        self.assertEqual(metrics["precision"], 1.0, "Cluster precision must be 1.0")
        self.assertEqual(metrics["recall"], 1.0, "Cluster recall must be 1.0")
        self.assertEqual(metrics["accuracy"], 1.0, "Cluster accuracy must be 1.0")


if __name__ == "__main__":
    unittest.main()
