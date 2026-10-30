"""Record a captured browser answer for a pre-created remaining formal run."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from b_runs import validate, validate_poc

ROOT = Path(__file__).resolve().parents[1]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--raw-output", required=True)
    ap.add_argument("--submitted-at", required=True)
    args = ap.parse_args()
    run = ROOT / "runs" / args.run_id
    raw = Path(args.raw_output).read_bytes()
    meta_path = run / "metadata.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    if sha((run / "input.txt").read_bytes()) != meta["input_sha256"]:
        raise SystemExit(f"input hash mismatch: {args.run_id}")
    obj, errors = validate(raw, meta["sample_id"], meta["vulnerability_type"], (run / "input.txt").read_bytes())
    poc_errors = validate_poc(raw, obj)
    (run / "raw_output.txt").write_bytes(raw)
    normalized = {
        "run_id": args.run_id,
        "format_valid": not errors,
        "format_errors": errors,
        "poc_format_valid": not poc_errors,
        "poc_format_errors": poc_errors,
        "parsed_json": obj,
        "human_verification": "pending",
        "raw_source": "DeepSeek web session",
    }
    (run / "normalized.json").write_text(json.dumps(normalized, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    meta.update(
        status="raw_recorded",
        model_display_name="DeepSeek-V4.1-Flash",
        model_settings="深度思考=开；联网搜索=关",
        submitted_at=args.submitted_at,
        recorded_at=datetime.now(timezone.utc).isoformat(),
        raw_output_sha256=sha(raw),
    )
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"run_id": args.run_id, "format_valid": not errors, "poc_format_valid": not poc_errors}, ensure_ascii=False))


if __name__ == "__main__":
    main()
