import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from tools.check_freeze import audit


VERSIONS = ("V0", "V1", "V2")
TEST_IDS = [
    *(f"S{number:03d}" for number in range(7, 13)),
    *(f"S{number:03d}" for number in range(19, 25)),
]
OWNER_BY_ID = {
    "S007": "A", "S008": "B", "S009": "C", "S010": "D",
    "S011": "D", "S012": "C", "S019": "B", "S020": "A",
    "S021": "A", "S022": "D", "S023": "C", "S024": "B",
}
REVIEWER_BY_OWNER = {"A": "D", "B": "A", "C": "B", "D": "C"}


def digest(data):
    return hashlib.sha256(data).hexdigest()


class FreezeAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "prompts").mkdir()
        (self.root / "dataset" / "packets").mkdir(parents=True)
        (self.root / "dataset" / "raw").mkdir(parents=True)
        (self.root / "evidence" / "truth").mkdir(parents=True)
        self.prompt_hashes = {}
        for vuln_type in ("SQLi", "XSS"):
            for version in VERSIONS:
                data = f"{vuln_type} {version} frozen prompt\n".encode()
                path = self.root / "prompts" / f"{vuln_type}_{version}.txt"
                path.write_bytes(data)
                self.prompt_hashes[(vuln_type, version)] = digest(data)
        self.manifest = self._manifest()
        self.runs = self._runs()

    def tearDown(self):
        self.temp.cleanup()

    def _manifest(self):
        result = []
        creators = {"SQL": "A", "XSS": "D"}
        for number in range(1, 25):
            sid = f"S{number:03d}"
            is_sql = number <= 12
            family_number = (number + 1) // 2 if is_sql else (number - 11) // 2
            vuln_type = "SQLi" if is_sql else "XSS"
            creator = creators["SQL" if is_sql else "XSS"]
            truth_reviewer = "C" if is_sql else "A"
            evidence = self.root / "evidence" / "truth" / f"{sid}.md"
            evidence.write_text("reviewed\n", encoding="utf-8")
            result.append({
                "sample_id": sid,
                "family_id": f"{'SQL' if is_sql else 'XSS'}{family_number:02d}",
                "vulnerability_type": vuln_type,
                "split": "test" if sid in TEST_IDS else "dev",
                "construction_target": "vulnerable" if number % 2 else "fixed",
                "creator": creator,
                "owner": OWNER_BY_ID.get(sid, ""),
                "case_code_sha256": "a" * 64,
                "ground_truth": bool(number % 2),
                "truth_reviewer": truth_reviewer,
                "truth_evidence": [f"evidence/truth/{sid}.md"],
                "status": "ready",
            })
        return result

    def _runs(self):
        runs = []
        for sid in TEST_IDS:
            number = int(sid[1:])
            vuln_type = "SQLi" if number <= 12 else "XSS"
            packet = f"<sample_id>{sid}</sample_id>\n<untrusted_code>\n</untrusted_code>\n".encode()
            packet_hash = digest(packet)
            directory = self.root / "dataset" / "packets" / f"{sid}_v1"
            directory.mkdir()
            (directory / "code_input.txt").write_bytes(packet)
            source_directory = self.root / "dataset" / "raw" / sid
            source_directory.mkdir()
            source = b"<?php\n"
            (source_directory / "index.php").write_bytes(source)
            (directory / "line_map.json").write_text(json.dumps({
                "sample_id": sid,
                "packet_sha256": packet_hash,
                "files": [{
                    "alias": "F01",
                    "source_file": "index.php",
                    "start": 1,
                    "end": 1,
                    "sha256": digest(source),
                }],
            }), encoding="utf-8")
            owner = OWNER_BY_ID[sid]
            for version in VERSIONS:
                runs.append({
                    "run_id": f"F_{sid}_{version}_R1",
                    "sample_id": sid,
                    "prompt_version": version,
                    "phase": "formal",
                    "status": "planned",
                    "operator": owner,
                    "reviewer": REVIEWER_BY_OWNER[owner],
                    "model_display_name": "Test Model Snapshot",
                    "packet_sha256": packet_hash,
                    "prompt_sha256": self.prompt_hashes[(vuln_type, version)],
                })
        return runs

    def test_complete_fixture_is_ready(self):
        report = audit(self.manifest, self.runs, self.root)
        self.assertTrue(report["ready"], report["blockers"])
        self.assertEqual(report["summary"]["formal_plan_records"], 36)
        self.assertEqual(
            report["artifacts"]["prompt_sha256"]["SQLi_V0"],
            self.prompt_hashes[("SQLi", "V0")],
        )

    def test_missing_truth_and_changed_prompt_are_blockers(self):
        self.manifest[0]["ground_truth"] = None
        path = self.root / "prompts" / "SQLi_V0.txt"
        path.write_text("changed after freeze\n", encoding="utf-8")
        report = audit(self.manifest, self.runs, self.root)
        codes = {item["code"] for item in report["blockers"]}
        self.assertFalse(report["ready"])
        self.assertIn("GROUND_TRUTH_NOT_REVIEWED", codes)
        self.assertIn("PROMPT_HASH_MISMATCH", codes)

    def test_packet_must_be_stable_across_prompt_versions(self):
        run = next(item for item in self.runs if item["run_id"] == "F_S007_V2_R1")
        run["packet_sha256"] = "b" * 64
        report = audit(self.manifest, self.runs, self.root)
        codes = {item["code"] for item in report["blockers"]}
        self.assertIn("PACKET_HASH_NOT_STABLE", codes)
        self.assertIn("PACKET_HASH_NOT_FOUND", codes)

    def test_line_map_source_hash_must_match_repository_file(self):
        path = self.root / "dataset" / "raw" / "S007" / "index.php"
        path.write_bytes(b"<?php\n// changed after packet generation\n")
        report = audit(self.manifest, self.runs, self.root)
        codes = {item["code"] for item in report["blockers"]}
        self.assertIn("SOURCE_HASH_MISMATCH", codes)

    def test_crlf_checkout_uses_canonical_lf_hashes(self):
        packet = self.root / "dataset" / "packets" / "S007_v1" / "code_input.txt"
        packet.write_bytes(packet.read_bytes().replace(b"\n", b"\r\n"))
        source = self.root / "dataset" / "raw" / "S007" / "index.php"
        source.write_bytes(source.read_bytes().replace(b"\n", b"\r\n"))
        report = audit(self.manifest, self.runs, self.root)
        self.assertTrue(report["ready"], report["blockers"])


if __name__ == "__main__":
    unittest.main()
