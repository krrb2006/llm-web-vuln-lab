#!/usr/bin/env python3
"""Read-only S001 binding checker for the eight INJ_SQLI rerun records.

Checks required files, prompt/input/raw hashes, session/screenshot binding,
model/settings fields, SAFE_BASE format, and duplicate screenshot artifacts.
Never edits any file.

Usage:
    python tools/check_s001_binding.py --root .
    python tools/check_s001_binding.py --root . --json
"""
import argparse
import hashlib
import json
import re
import struct
import sys
from datetime import datetime
from pathlib import Path

RUNS = [
    "INJ_SQLI_IGNORE_BASE", "INJ_SQLI_IGNORE_DEF",
    "INJ_SQLI_SAFE_BASE", "INJ_SQLI_SAFE_DEF",
    "INJ_SQLI_LEAK_BASE", "INJ_SQLI_LEAK_DEF",
    "INJ_SQLI_DIVERT_BASE", "INJ_SQLI_DIVERT_DEF",
]
HEX64 = re.compile(r"^[0-9a-fA-F]{64}$")


def sha_lf(path):
    data = path.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def png_ok(path):
    try:
        with open(path, "rb") as f:
            return f.read(8) == b"\x89PNG\r\n\x1a\n"
    except OSError:
        return False


def check_run(root, run_id, prompt_hashes):
    d = root / "runs" / run_id
    issues = []
    warnings = []
    meta_p = d / "metadata.json"
    norm_p = d / "normalized.json"
    input_p = d / "input.txt"
    raw_candidates = [d / "raw_output_user.txt", d / "raw_output_rerun.txt", d / "raw_output.txt"]
    raw_hashes = {p.name: sha_lf(p) for p in raw_candidates if p.exists()}

    for p in (meta_p, norm_p, input_p):
        if not p.exists():
            issues.append(f"missing {p.name}")
    if not raw_hashes:
        issues.append("missing raw_output_user.txt / raw_output_rerun.txt / raw_output.txt")
    if issues:
        return {"run_id": run_id, "status": "FAIL", "issues": issues, "warnings": warnings}

    meta = json.loads(meta_p.read_text(encoding="utf-8"))
    norm = json.loads(norm_p.read_text(encoding="utf-8"))
    parsed = norm.get("parsed_json") or {}

    # Hashes: prompt, input, raw
    prompt_hash = meta.get("prompt_sha256", "")
    if prompt_hash not in prompt_hashes.values():
        issues.append("prompt_sha256 not in environment/prompt_hashes.txt")
    if not HEX64.match(str(prompt_hash)):
        issues.append("prompt_sha256 is not 64 hex")

    input_hash = meta.get("input_sha256", "")
    if not HEX64.match(str(input_hash)):
        issues.append("input_sha256 is not 64 hex")
    elif sha_lf(input_p) != input_hash.lower():
        issues.append("input_sha256 does not match input.txt")

    canonical = meta.get("raw_output_sha256")
    alias = meta.get("raw_output_user_sha256")
    raw_file = None
    if canonical:
        if not HEX64.match(str(canonical)):
            issues.append("raw_output_sha256 is not 64 hex")
        else:
            matched = [name for name, h in raw_hashes.items() if h == canonical.lower()]
            if not matched:
                issues.append("raw_output_sha256 matches none of: " + ", ".join(f"{k}={v[:12]}" for k, v in raw_hashes.items()))
            else:
                raw_file = matched[0]
    elif alias:
        warnings.append("raw_output_sha256 missing; only raw_output_user_sha256 alias")
        if not HEX64.match(str(alias)):
            issues.append("raw_output_user_sha256 is not 64 hex")
        else:
            matched = [name for name, h in raw_hashes.items() if h == alias.lower()]
            if not matched:
                issues.append("raw_output_user_sha256 matches no raw file")
            else:
                raw_file = matched[0]
    else:
        issues.append("both raw_output_sha256 and raw_output_user_sha256 missing")

    # Session binding
    canonical_sess = meta.get("session_url")
    alias_sess = meta.get("rerun_session_url")
    if not canonical_sess and not alias_sess:
        issues.append("no session_url / rerun_session_url")
    elif not canonical_sess:
        warnings.append("session_url missing; only rerun_session_url alias")

    # Model/settings
    if not meta.get("model_display_name"):
        issues.append("model_display_name is null/empty")
    if not meta.get("model_settings"):
        issues.append("model_settings is empty")
    settings = meta.get("settings_screenshot")
    if not settings:
        issues.append("settings_screenshot missing")
    elif not (root / settings).exists():
        issues.append(f"settings_screenshot not found: {settings}")
    elif not png_ok(root / settings):
        warnings.append("settings_screenshot is not a PNG")

    shot = meta.get("rerun_screenshot")
    if not shot:
        issues.append("rerun_screenshot missing")
    elif not (root / shot).exists():
        issues.append(f"rerun_screenshot not found: {shot}")
    elif not png_ok(root / shot):
        warnings.append("rerun_screenshot is not a PNG")

    # Time / POC
    rerun_at = meta.get("rerun_at")
    if not rerun_at:
        warnings.append("rerun_at missing")
    else:
        try:
            datetime.fromisoformat(str(rerun_at).replace("Z", "+00:00"))
        except ValueError:
            warnings.append(f"rerun_at is not full ISO time: {rerun_at}")
    if meta.get("poc_executed") is not False:
        issues.append("poc_executed is not false")

    # Normalized consistency
    if run_id.endswith("SAFE_BASE"):
        if norm.get("format_valid") is not False:
            issues.append("SAFE_BASE format_valid must be false")
    else:
        if norm.get("format_valid") is not True:
            issues.append("format_valid is not true")
    if parsed.get("prediction") != "vulnerable":
        issues.append(f"prediction is not vulnerable: {parsed.get('prediction')}")

    # Screenshot duplicate artifact
    dup = root / "evidence" / "user_S001_rerun_screenshots" / "007_answer_duplicate.png"
    if dup.exists():
        warnings.append("007_answer_duplicate.png still present")

    status = "FAIL" if issues else ("WARN" if warnings else "PASS")
    return {
        "run_id": run_id, "status": status, "issues": issues,
        "warnings": warnings, "raw_file": raw_file,
        "canonical_raw_hash": bool(canonical), "canonical_session": bool(canonical_sess),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    root = Path(args.root).resolve()
    prompt_file = root / "environment" / "prompt_hashes.txt"
    prompt_hashes = {}
    if prompt_file.exists():
        for line in prompt_file.read_text(encoding="utf-8").splitlines():
            parts = line.split()
            if len(parts) == 2:
                prompt_hashes[parts[0]] = parts[1].lower()
    rows = [check_run(root, r, prompt_hashes) for r in RUNS]
    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
    else:
        print("| run_id | status | issues | warnings |")
        print("|---|---|---|---|")
        for r in rows:
            print(f"| {r['run_id']} | {r['status']} | {'; '.join(r['issues']) or '-'} | {'; '.join(r['warnings']) or '-'} |")
    return 1 if any(r["status"] == "FAIL" for r in rows) else 0


if __name__ == "__main__":
    sys.exit(main())
