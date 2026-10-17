import unittest

from tools.audit_submission import EXPECTED_BONUS, validate_bonus_plan


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


if __name__ == "__main__":
    unittest.main()
