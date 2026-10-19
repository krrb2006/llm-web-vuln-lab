#!/usr/bin/env python3
"""Normalize one context-ablation model answer without executing any POC."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from b_runs import validate, validate_poc


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--raw-output", required=True)
    parser.add_argument("--submitted-at", required=True)
    args = parser.parse_args()

    run_dir = ROOT / "experiments" / "context_ablation" / "runs" / args.run_id
    raw_path = ROOT / args.raw_output
    raw = raw_path.read_bytes()
    metadata = json.loads((run_dir / "metadata.json").read_text(encoding="utf-8"))
    parsed, format_errors = validate(
        raw,
        metadata["sample_id"],
        "XSS",
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
    (run_dir / "normalized.json").write_text(json.dumps(normalized, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    metadata_path = run_dir / "metadata.json"
    metadata.update(
        {
            "status": "executed_pending_review",
            "model_display_name": "DeepSeek-V4.1-Flash",
            "model_settings": "深度思考=开；联网搜索=关",
            "submitted_at": args.submitted_at,
            "raw_output_sha256": hashlib.sha256(raw).hexdigest(),
        }
    )
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"run_id": args.run_id, "format_valid": not format_errors, "poc_format_valid": not poc_errors}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
