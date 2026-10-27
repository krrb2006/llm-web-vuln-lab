import json
import tempfile
import unittest
from pathlib import Path

from tools.audit_submission import (
    EXPECTED_BONUS,
    validate_bonus_plan,
    validate_model_provenance,
)


class SubmissionAuditTests(unittest.TestCase):
    def _valid_plan(self):
        records = []
        for category, count in EXPECTED_BONUS.items():
            for number in range(count):
                records.append({
                    "run_id": f"{category}_{number}",
                    "category": category,
                    "status": "planned",
                    "operator": "A",
                    "reviewer": "D",
                })
        return records

    def test_expected_bonus_plan_is_valid(self):
        self.assertEqual(validate_bonus_plan(self._valid_plan()), [])

    def test_duplicate_and_self_review_are_rejected(self):
        records = self._valid_plan()
        records[1]["run_id"] = records[0]["run_id"]
        records[2]["reviewer"] = "A"
        issues = validate_bonus_plan(records)
        self.assertTrue(any("duplicate" in item for item in issues))
        self.assertTrue(any("must differ" in item for item in issues))

    def test_announcement_inference_is_not_per_run_proof(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            metadata = root / "evidence" / "run" / "metadata.json"
            metadata.parent.mkdir(parents=True)
            metadata.write_text(json.dumps({
                "model_version_proven": True,
                "per_run_model_field_captured": False,
            }), encoding="utf-8")
            records = [{
                "run_id": "INJ_SQLI_TEST",
                "evidence_paths": ["evidence/run/metadata.json"],
            }]
            issues = validate_model_provenance(root, records)
            self.assertTrue(any("cannot be proven" in item for item in issues))

            metadata.write_text(json.dumps({
                "model_version_proven": False,
                "model_version_inferred": "DeepSeek-V4.1-Flash-1017",
                "per_run_model_field_captured": False,
            }), encoding="utf-8")
            self.assertEqual(validate_model_provenance(root, records), [])


if __name__ == "__main__":
    unittest.main()
