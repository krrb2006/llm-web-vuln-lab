import tempfile
import unittest
from pathlib import Path

from tools.evaluate import summarize


class EvaluateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "evidence").mkdir()
        self.manifest = []
        for sample_id, truth, vulnerability_type in (
            ("S007", True, "SQLi"),
            ("S008", False, "SQLi"),
            ("S019", True, "XSS"),
            ("S020", False, "XSS"),
        ):
            truth_path = self.root / "evidence" / f"truth-{sample_id}.md"
            truth_path.write_text("reviewed\n", encoding="utf-8")
            self.manifest.append({
                "sample_id": sample_id,
                "split": "test",
                "owner": "A",
                "ground_truth": truth,
                "truth_reviewer": "D",
                "truth_evidence": [f"evidence/truth-{sample_id}.md"],
                "vulnerability_type": vulnerability_type,
            })

    def tearDown(self):
        self.temp.cleanup()

    def _run(self, sample_id, version, prediction, location=None):
        evidence = self.root / "evidence" / f"{sample_id}-{version}.md"
        evidence.write_text("reviewed\n", encoding="utf-8")
        return {
            "run_id": f"F_{sample_id}_{version}_R1",
            "sample_id": sample_id,
            "prompt_version": version,
            "phase": "formal",
            "status": "reviewed",
            "operator": "A",
            "reviewer": "D",
            "prediction": prediction,
            "location_correct": location,
            "poc_generated": prediction == "vulnerable",
            "raw_execution_ok": False,
            "environment_execution_ok": False,
            "logic_changed": False,
            "verification": "not_run",
            "evidence_paths": [f"evidence/{sample_id}-{version}.md"],
        }

    def test_rich_metrics_and_paired_improvement(self):
        runs = []
        predictions = {
            "V0": {"S007": "safe", "S008": "vulnerable", "S019": "safe", "S020": "safe"},
            "V1": {"S007": "vulnerable", "S008": "safe", "S019": "safe", "S020": "safe"},
            "V2": {"S007": "vulnerable", "S008": "safe", "S019": "vulnerable", "S020": "safe"},
        }
        for version, values in predictions.items():
            for sample_id, prediction in values.items():
                runs.append(self._run(
                    sample_id,
                    version,
                    prediction,
                    True if prediction == "vulnerable" else None,
                ))
        result = summarize(self.manifest, runs, self.root)
        self.assertTrue(result["complete"])
        self.assertEqual(result["by_version"]["V2"]["all_sample_accuracy"], 1.0)
        self.assertEqual(result["by_type"]["V2"]["XSS"]["N"], 2)
        comparison = result["pairwise"]["V0_to_V2"]
        self.assertEqual(comparison["resolved_error"], 3)
        self.assertEqual(comparison["regression"], 0)
        self.assertEqual(comparison["accuracy_delta"], 0.75)

    def test_vulnerable_prediction_requires_location_review(self):
        runs = [self._run("S007", "V0", "vulnerable", None)]
        with self.assertRaisesRegex(ValueError, "location_correct"):
            summarize(self.manifest, runs, self.root, allow_partial=True)


if __name__ == "__main__":
    unittest.main()
