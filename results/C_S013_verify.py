"""Read-only verification of A's eight official S013 injection records.

Runs only local file checks. Never invokes a model or executes a generated POC.
"""
from __future__ import annotations

import difflib
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((ROOT / "experiments/prompt_injection/official_packets/S013/manifest.json").read_text(encoding="utf-8"))
PLAN = json.loads((ROOT / "experiments/bonus_runs.plan.json").read_text(encoding="utf-8"))
PLAN = {row["run_id"]: row for row in PLAN if row["run_id"].startswith("INJ_XSS_")}
FREEZE = dict(line.split() for line in (ROOT / "environment/prompt_hashes.txt").read_text(encoding="utf-8").splitlines())
ATTACKS = {
    "IGNORE": "ignore_task",
    "SAFE": "force_safe_verdict",
    "LEAK": "request_hidden_rules",
    "DIVERT": "divert_output",
}
REQUIRED = ("input.txt", "raw_output.txt", "metadata.json", "normalized.json", "settings_response.png")
CODE_LINE = re.compile(r"^F01:(\d{4}) \| (.*)$")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_hash(path: Path) -> str:
    return digest(path.read_bytes())


def no_duplicate_pairs(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError(f"duplicate JSON key: {key}")
        out[key] = value
    return out


def first_json(raw: str):
    start = raw.find("{")
    if start < 0:
        raise ValueError("no JSON object")
    return json.JSONDecoder(object_pairs_hook=no_duplicate_pairs).raw_decode(raw[start:])[0]


def extract_php(packet: Path) -> bytes:
    lines = packet.read_text(encoding="utf-8").splitlines()
    code = []
    for line in lines:
        match = CODE_LINE.fullmatch(line)
        if match:
            if int(match.group(1)) != len(code) + 1:
                raise ValueError(f"noncontiguous F01 numbering: {packet}")
            code.append(match.group(2))
    if len(code) != 15 or not code[0].startswith("<?php"):
        raise ValueError(f"unexpected code wrapper: {packet}")
    return ("\n".join(code) + "\n").encode("utf-8")


def main():
    original_packet = ROOT / MANIFEST["source_path"]
    original_php = extract_php(original_packet)
    php_binary = shutil.which("php")
    runtime_evidence_path = ROOT / "results" / "C_S013_runtime_regression.json"
    runtime_evidence = json.loads(runtime_evidence_path.read_text(encoding="utf-8")) if runtime_evidence_path.is_file() else {}
    result = {
        "audit_base": "origin/a/criteria-and-sql01@5927ec8375dfeb28ec72ea3b154d6849a008c332",
        "source_packet_sha256": file_hash(original_packet),
        "source_php_sha256": digest(original_php),
        "php_binary": php_binary,
        "runtime_evidence_path": "results/C_S013_runtime_regression.json" if runtime_evidence else None,
        "attacks": {},
        "runs": {},
    }
    assert result["source_packet_sha256"] == MANIFEST["source_sha256"]
    with tempfile.TemporaryDirectory(prefix="s013_audit_") as temp:
        temp_dir = Path(temp)
        for short, attack in ATTACKS.items():
            entry = MANIFEST["attacks"][attack]
            packet = ROOT / entry["packet_path"]
            modified_php = extract_php(packet)
            diff = list(difflib.unified_diff(
                original_php.decode().splitlines(),
                modified_php.decode().splitlines(),
                lineterm="",
            ))
            expected_comment = "// 读取搜索词参数 q；" + entry["text"]
            only_comment_changed = (
                len(diff) > 0
                and modified_php.splitlines()[1].decode() == expected_comment
                and original_php.splitlines()[:1] + original_php.splitlines()[2:]
                == modified_php.splitlines()[:1] + modified_php.splitlines()[2:]
            )
            raw_php_path = temp_dir / f"{attack}.php"
            raw_php_path.write_bytes(modified_php)
            if php_binary:
                proc = subprocess.run([php_binary, "-l", str(raw_php_path)], capture_output=True, text=True)
                lint = {"status": "pass" if proc.returncode == 0 else "fail", "returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}
            else:
                lint = {"status": "unavailable", "reason": "php executable not found; no php -l performed"}
            runtime_package = runtime_evidence.get("packages", {}).get(attack, {})
            if runtime_package.get("php_lint"):
                lint = runtime_package["php_lint"]
            result["attacks"][attack] = {
                "packet_path": entry["packet_path"],
                "packet_sha256": file_hash(packet),
                "packet_hash_matches_manifest": file_hash(packet) == entry["packet_sha256"],
                "php_sha256": digest(modified_php),
                "only_php_comment_line_2_changed": only_comment_changed,
                "diff": diff,
                "php_lint": lint,
                "normal_business_runtime": runtime_package.get("normal_http", "not_run"),
            }
            for condition, version, suffix in (("baseline", "V0", "BASE"), ("defended", "V2", "DEF")):
                run_id = f"INJ_XSS_{short}_{suffix}"
                run = ROOT / "runs" / f"{run_id}_R1"
                meta = json.loads((run / "metadata.json").read_text(encoding="utf-8"))
                normalized = json.loads((run / "normalized.json").read_text(encoding="utf-8"))
                prompt = ROOT / "prompts" / f"XSS_{version}.txt"
                prompt_text = prompt.read_text(encoding="utf-8").replace("\r\n", "\n")
                packet_text = packet.read_text(encoding="utf-8").replace("\r\n", "\n")
                expected_input = (prompt_text + "\n" + packet_text).encode("utf-8")
                actual_input = (run / "input.txt").read_bytes()
                prompt_bytes = prompt.read_bytes()
                packet_bytes = packet.read_bytes()
                input_embeds_both = actual_input.startswith(prompt_bytes) and actual_input.endswith(packet_bytes)
                separator = actual_input[len(prompt_bytes):len(actual_input) - len(packet_bytes)] if input_embeds_both else b""
                raw_text = (run / "raw_output.txt").read_text(encoding="utf-8")
                try:
                    parsed_raw = first_json(raw_text)
                    strict_error = None
                except (json.JSONDecodeError, ValueError) as exc:
                    parsed_raw = None
                    strict_error = str(exc)
                try:
                    permissive_raw = json.JSONDecoder().raw_decode(raw_text[raw_text.find("{"):])[0]
                    syntax_error = None
                except (json.JSONDecodeError, ValueError) as exc:
                    permissive_raw = None
                    syntax_error = str(exc)
                hashes = {
                    "prompt": file_hash(prompt),
                    "packet": file_hash(packet),
                    "input": file_hash(run / "input.txt"),
                    "raw_output": file_hash(run / "raw_output.txt"),
                }
                evidence_paths = PLAN[run_id]["evidence_paths"]
                result["runs"][run_id] = {
                    "directory": str(run.relative_to(ROOT)).replace("\\", "/"),
                    "attack": attack,
                    "condition": condition,
                    "prompt_version": version,
                    "hashes": hashes,
                    "hashes_match_metadata": {
                        key: hashes[key] == meta[f"{key}_sha256"] for key in hashes
                    },
                    "prompt_matches_metadata": hashes["prompt"] == meta["prompt_sha256"],
                    "prompt_matches_freeze": hashes["prompt"] == FREEZE[f"XSS_{version}"],
                    "freeze_registry_value": FREEZE[f"XSS_{version}"],
                    "input_exact_composition_as_preparer_documented": actual_input == expected_input,
                    "input_embeds_prompt_and_packet_byte_exact": input_embeds_both,
                    "input_separator_hex": separator.hex(),
                    "meta_fields_match": all((
                        meta["run_id"] == run_id,
                        meta["attack"] == attack,
                        meta["condition"] == condition,
                        meta["prompt_version"] == version,
                        meta["source_code_input"] == entry["packet_path"],
                        meta["sample_id"] == "S013",
                        meta["status"] == "executed_pending_review",
                    )),
                    "plan_fields_match": all((
                        PLAN[run_id]["attack"] == attack,
                        PLAN[run_id]["condition"] == condition,
                        PLAN[run_id]["prompt_version"] == version,
                        PLAN[run_id]["status"] == "executed",
                        PLAN[run_id]["operator"] == "C",
                        PLAN[run_id]["reviewer"] == "B",
                    )),
                    "all_evidence_paths_exist": all((ROOT / path).is_file() for path in evidence_paths),
                    "required_files_exist": all((run / name).is_file() for name in REQUIRED),
                    "model_display_name": meta["model_display_name"],
                    "model_settings_recorded": meta["model_settings"],
                    "actual_operator": meta["operator"],
                    "submitted_at": meta["submitted_at"],
                    "recorded_at": meta["recorded_at"],
                    "strict_raw_json_valid": strict_error is None,
                    "strict_raw_json_error": strict_error,
                    "raw_json_syntax_valid_ignoring_duplicate_keys": syntax_error is None,
                    "raw_json_syntax_error": syntax_error,
                    "permissive_parsed_raw_matches_normalized": permissive_raw == normalized.get("parsed_json") if permissive_raw is not None else None,
                    "parsed_raw_matches_normalized": parsed_raw == normalized.get("parsed_json") if parsed_raw is not None else None,
                    "normalized_format_valid": normalized.get("format_valid"),
                    "normalized_poc_format_valid": normalized.get("poc_format_valid"),
                    "normalized_prediction": normalized.get("parsed_json", {}).get("prediction"),
                    "human_verification": normalized.get("human_verification"),
                }
    out = ROOT / "results/C_S013_independent_audit.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(out)
    print(f"runs={len(result['runs'])}, strict_raw_json_valid={sum(r['strict_raw_json_valid'] for r in result['runs'].values())}")
    for run_id, row in result["runs"].items():
        print(run_id, "hashes=" + str(all(row["hashes_match_metadata"].values())), "strict_json=" + str(row["strict_raw_json_valid"]), row["strict_raw_json_error"] or "")


if __name__ == "__main__":
    main()
