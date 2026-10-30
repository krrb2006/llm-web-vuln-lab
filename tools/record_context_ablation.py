#!/usr/bin/env python3
"""Normalize one context-ablation model answer without executing any POC."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from b_runs import validate, validate_poc


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_TYPES = {"S007": "SQLi", "S020": "XSS"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument(
        "--run-dir",
        help="override the archive directory, e.g. prepared_sqliv2_rerun/<run_id>",
    )
    parser.add_argument("--raw-output", required=True)
    parser.add_argument("--submitted-at")
    parser.add_argument("--time-note", help="use when the UI does not export an exact submission timestamp")
    args = parser.parse_args()

    if not args.submitted_at and not args.time_note:
        raise SystemExit("provide --submitted-at or --time-note")

    run_dir = (
        (ROOT / args.run_dir)
        if args.run_dir
        else ROOT / "experiments" / "context_ablation" / "runs" / args.run_id
    )
    raw_path = ROOT / args.raw_output
    raw = raw_path.read_bytes()
    metadata = json.loads((run_dir / "metadata.json").read_text(encoding="utf-8"))
    sample_id = metadata["sample_id"]
    expected_type = EXPECTED_TYPES.get(sample_id)
    if expected_type is None:
        raise SystemExit(f"unsupported context-ablation sample: {sample_id}")
    if metadata.get("prompt_family") and metadata["prompt_family"] != expected_type:
        raise SystemExit(
            f"prompt family mismatch for {sample_id}: "
            f"{metadata['prompt_family']} != {expected_type}"
        )
    parsed, format_errors = validate(
        raw,
        sample_id,
        expected_type,
        (run_dir / "input.txt").read_bytes(),
    )
    poc_errors = validate_poc(raw, parsed)
    normalized = {
        "run_id": args.run_id,
        "format_valid": not format_errors,
        "format_errors": format_errors,
        "poc_format_valid": not poc_errors,
        "poc_format_errors": poc_errors,
        "parsed_json": parsed,
        "human_verification": "pending",
        "raw_source": "DeepSeek web session",
    }
    (run_dir / "raw_output.txt").write_bytes(raw)
    (run_dir / "normalized.json").write_text(json.dumps(normalized, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    metadata_path = run_dir / "metadata.json"
    metadata.update(
        {
            "status": "executed_pending_review",
            "model_display_name": "DeepSeek-V4.1-Flash",
            "model_settings": "深度思考=开；联网搜索=关",
            "submitted_at": args.submitted_at,
            "submission_time_note": args.time_note,
            "raw_output_sha256": hashlib.sha256(raw).hexdigest(),
        }
    )
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"run_id": args.run_id, "format_valid": not format_errors, "poc_format_valid": not poc_errors}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
