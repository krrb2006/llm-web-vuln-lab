#!/usr/bin/env python3
"""Read-only S001 official injection audit. Never executes model POCs."""
import hashlib
import ast
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNS = [
    ("IGNORE", "ignore_task"), ("SAFE", "force_safe_verdict"),
    ("LEAK", "request_hidden_rules"), ("DIVERT", "divert_output"),
]
REQUIRED = {
    "sample_id": str, "prediction": str, "vulnerability_type": str,
    "locations": list, "evidence": dict, "prerequisites": list,
    "missing_context": list, "poc_generated": bool,
    "poc_language": str, "poc_instructions": str,
}
def data(path):
    p = ROOT / path
    return p.read_bytes() if p.is_file() else None
def sha(value):
    return hashlib.sha256(value).hexdigest() if value is not None else None
def parse_raw(value):
    if value is None:
        return None, ["raw output missing"], ""
    s = value.decode("utf-8-sig")
    start = s.find("{")
    if start < 0:
        return None, ["JSON object missing"], s
    duplicate = []
    def pairs(items):
        out = {}
        for key, val in items:
            if key in out:
                duplicate.append(key)
            out[key] = val
        return out
    try:
        parsed, end = json.JSONDecoder(object_pairs_hook=pairs).raw_decode(s[start:])
        return parsed, duplicate, s[start + end:]
    except json.JSONDecodeError as exc:
        return None, [str(exc)], s
def extract_php(packet):
    text = packet.decode("utf-8")
    rows = []
    for line in text.splitlines():
        match = re.match(r"F01:(\d{4}) \|(?: ?)(.*)$", line)
        if match:
            rows.append((int(match.group(1)), match.group(2)))
    return rows
def main():
    plan = {e["run_id"]: e for e in json.loads(data("experiments/bonus_runs.plan.json"))}
    source = data("dataset/packets/S001_v1/code_input.txt")
    source_rows = extract_php(source)
    result = {
        "audit_kind": "C independent read-only review of B official S001 SQLi injection",
        "base_commit": "cdf6264fd14f76bfa2a47b3e6381d11b8344f5e7",
        "poc_executed_by_audit": False,
        "source_packet_sha256": sha(source),
        "runs": {}, "packets": {},
    }
    for short, attack in RUNS:
        packet_path = f"experiments/prompt_injection/official_packets/S001/{attack}/code_input.txt"
        packet = data(packet_path)
        rows = extract_php(packet)
        changes = [{"line": n, "source": a, "injected": b}
                   for (n, a), (m, b) in zip(source_rows, rows) if n != m or a != b]
        result["packets"][attack] = {
            "path": packet_path, "sha256": sha(packet),
            "line_count_matches": len(rows) == len(source_rows) == 24,
            "changed_lines": changes,
            "only_comment_line_3_changed": len(changes) == 1 and changes[0]["line"] == 3
                and source_rows[1][1].strip() == "/**" and source_rows[3][1].strip() == "*/",
            "executable_lines_equal": all(a == b for (n, a), (_, b) in zip(source_rows, rows) if n != 3),
        }
        for cond, version in [("BASE", "V0"), ("DEF", "V2")]:
            rid = f"INJ_SQLI_{short}_{cond}"
            prefix = f"runs/{rid}/"
            meta = json.loads(data(prefix + "metadata.json"))
            norm = json.loads(data(prefix + "normalized.json"))
            raw_bytes = data(prefix + "raw_output.txt")
            raw, duplicates, suffix = parse_raw(raw_bytes)
            prompt_path = f"prompts/SQLi_{version}.txt"
            prompt = data(prompt_path)
            missing = [k for k, typ in REQUIRED.items()
                       if raw is None or k not in raw or not isinstance(raw[k], typ)]
            evidence = raw.get("evidence") if isinstance(raw, dict) else None
            evidence_missing = [k for k in ("source", "flow", "guard", "sink")
                                if not isinstance(evidence, dict) or not isinstance(evidence.get(k), str)]
            remainder = suffix.lower()
            has_python_block = (chr(96) * 3 + "python") in remainder
            python_blocks = re.findall(chr(96) * 3 + r"(?:python|python3)\s*\n(.*?)" + chr(96) * 3,
                                       suffix, flags=re.I | re.S)
            python_syntax_valid = True
            for block in python_blocks:
                try:
                    ast.parse(block)
                except SyntaxError:
                    python_syntax_valid = False
            poc_format = None if raw is None else (
                not missing and python_syntax_valid and
                ((not raw.get("poc_generated") and not has_python_block)
                or (raw.get("poc_generated") and
                    (has_python_block or raw.get("poc_language") == "manual")))
            )
            screenshot = meta.get("settings_screenshot")
            conclusion = "不通过" if missing or evidence_missing else "待补证"
            result["runs"][rid] = {
                "attack": attack, "condition": meta.get("condition"),
                "prompt_version": version,
                "plan_fields_match": all([
                    plan[rid]["attack"] == attack,
                    plan[rid]["condition"] == ("baseline" if cond == "BASE" else "defended"),
                    plan[rid]["prompt_version"] == version,
                    meta.get("run_id") == rid, meta.get("sample_id") == "S001"]),
                "plan_status": plan[rid]["status"],
                "plan_reviewer": plan[rid]["reviewer"],
                "plan_evidence_paths": plan[rid]["evidence_paths"],
                "prompt_sha256": sha(prompt),
                "prompt_matches_metadata": sha(prompt) == meta.get("prompt_sha256"),
                "packet_sha256": sha(packet),
                "packet_matches_metadata": sha(packet) == meta.get("input_packet_sha256"),
                "raw_output_sha256": sha(raw_bytes),
                "raw_hash_in_metadata": meta.get("raw_output_sha256"),
                "input_txt_exists": data(prefix + "input.txt") is not None,
                "strict_unique_json": raw is not None and not duplicates,
                "duplicate_keys": duplicates,
                "required_fields_missing_or_wrong_type": missing,
                "evidence_fields_missing": evidence_missing,
                "prediction": raw.get("prediction") if raw else None,
                "normalized_matches_parsed_raw": raw == norm.get("parsed_json"),
                "normalized_format_valid": norm.get("format_valid"),
                "poc_format_by_audit": poc_format,
                "python_code_block_count": len(python_blocks),
                "python_code_syntax_valid_without_execution": python_syntax_valid,
                "poc_executed_metadata": meta.get("poc_executed"),
                "poc_executed_normalized": norm.get("poc_executed"),
                "screenshot_path": screenshot,
                "screenshot_exists": data(screenshot) is not None if screenshot else False,
                "model_display_name": meta.get("model_display_name"),
                "conclusion": conclusion,
                "conclusion_scope": "原文必需字段及当前归档完整性；不代表 POC 触发",
            }
    out = ROOT / "results/C_S001_official_independent_audit.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(out)
if __name__ == "__main__":
    main()
