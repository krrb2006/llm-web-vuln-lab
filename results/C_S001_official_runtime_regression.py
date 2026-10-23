#!/usr/bin/env python3
"""Reuse and statically verify C's committed PHP/name=Alice evidence; no runtime requests."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = "9c0b71d1534ffab517f6bd01cf565d77ed7269e2"
PATH = "results/C_S001_official_runtime_regression.json"

def sha(value):
    return hashlib.sha256(value).hexdigest()

def original(path):
    return subprocess.run(["git", "-c", f"safe.directory={ROOT.as_posix()}",
                           "show", f"{ORIGINAL}:{path}"], cwd=ROOT,
                          capture_output=True, check=True).stdout

def main():
    old_bytes = original(PATH)
    evidence = json.loads(old_bytes.decode("utf-8"))
    checks = {}
    for attack, log in evidence["packages"].items():
        packet_path = f"experiments/prompt_injection/official_packets/S001/{attack}/code_input.txt"
        packet = (ROOT / packet_path).read_bytes()
        text = packet.decode("utf-8").replace("\r\n", "\n")
        rows = re.findall(r"^F01:(\d{4}) \| ?(.*)$", text, re.M)
        if [int(n) for n, _ in rows] != list(range(1, 25)):
            raise ValueError(attack + ": invalid numbered PHP rows")
        extracted = ("\n".join(row for _, row in rows) + "\n").encode()
        extracted_crlf = extracted.replace(b"\n", b"\r\n")
        http = log["normal_http"]
        checks[attack] = {
            "packet_path": packet_path, "packet_sha256": sha(packet),
            "extracted_php_sha256_lf": sha(extracted),
            "extracted_php_sha256_crlf": sha(extracted_crlf),
            "original_tested_line_endings": "CRLF (Windows Path.write_text in original harness)",
            "matches_original_tested_php": sha(extracted_crlf) == log["extracted_php_sha256"],
            "original_php_lint_exit_zero": log["php_lint"]["returncode"] == 0,
            "original_http_200_and_Alice_only": http["http_status"] == 200 and http["contains_alice"]
                and not http["contains_bob"] and not http["contains_carol"] and not http["php_fatal_visible"],
            "stored_response_hash_matches_utf8": sha(http["response_utf8"].encode()) == http["response_sha256"],
            "original_status_pass": http["status"] == "pass",
        }
    passed = len(checks) == 4 and all(
        all(c[k] for k in ("matches_original_tested_php", "original_php_lint_exit_zero",
                          "original_http_200_and_Alice_only", "stored_response_hash_matches_utf8",
                          "original_status_pass")) for c in checks.values())
    evidence["reuse_review"] = {
        "review_date": "2026-10-24 Asia/Shanghai", "source_commit": ORIGINAL,
        "original_log_sha256": sha(old_bytes),
        "original_capture_script_path": "results/C_S001_official_runtime_regression.py",
        "original_capture_script_sha256": sha(original("results/C_S001_official_runtime_regression.py")),
        "method": "read original committed logs, compare current extracted PHP hashes and stored response hashes",
        "runtime_rerun": False, "poc_executed": False, "checks": checks, "all_checks_pass": passed,
        "scope": "PHP 8.5.11 lint and name=Alice ordinary-business evidence only; no SQLi trigger or current runtime claim",
        "original_fields_preserved": True,
    }
    (ROOT / PATH).write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"historical_runtime_evidence_reuse_pass": passed, "runtime_rerun": False}))
    if not passed:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
