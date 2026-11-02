"""Unit test wrapper for labeled-set citation verification evaluation."""
import unittest
from tests.run_labeled_eval import run_evaluation


class TestLabeledSetEval(unittest.TestCase):
    def test_precision_recall_100_percent(self):
        metrics = run_evaluation()
        self.assertEqual(metrics["total"], 12)
        self.assertEqual(metrics["precision"], 1.0)
        self.assertEqual(metrics["recall"], 1.0)
        self.assertEqual(metrics["accuracy"], 1.0)


if __name__ == "__main__":
    unittest.main()
