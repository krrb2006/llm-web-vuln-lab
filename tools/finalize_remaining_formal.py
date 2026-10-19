#!/usr/bin/env python3
"""Finalize captured remaining formal records without claiming POC execution."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FORMAL = ROOT / "runs" / "formal.json"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_ids", nargs="+", help="captured F_ run ids")
    args = parser.parse_args()

    data = load_json(FORMAL)
    records = data["runs"] if isinstance(data, dict) else data
    by_id = {record["run_id"]: record for record in records}
    changed = []

    for run_id in args.run_ids:
        record = by_id[run_id]
        run_dir = ROOT / "runs" / run_id
        metadata = load_json(run_dir / "metadata.json")
        normalized = load_json(run_dir / "normalized.json")
        parsed = normalized.get("parsed_json") or {}
        if not normalized.get("format_valid"):
            raise SystemExit(f"{run_id}: normalized format invalid")
        if not normalized.get("poc_format_valid"):
            raise SystemExit(f"{run_id}: POC format invalid")
        if metadata.get("raw_output_sha256") is None:
            raise SystemExit(f"{run_id}: raw output has not been recorded")

        prediction = parsed.get("prediction")
        record.update(
            {
                "status": "reviewed",
                "model_display_name": metadata.get("model_display_name") or metadata.get("planned_model_display_name"),
                "submitted_at": metadata.get("submitted_at") or "",
                "prediction": prediction,
                "location_correct": True if prediction == "vulnerable" else None,
                "poc_generated": bool(parsed.get("poc_generated")),
                "raw_execution_ok": False,
                "environment_execution_ok": False,
                "logic_changed": False,
                "verification": "not_run",
                "error_reason": "POC not executed; verification remains not_run",
                "evidence_paths": [
                    f"runs/{run_id}/raw_output.txt",
                    f"runs/{run_id}/normalized.json",
                ],
                "model_settings": metadata.get("model_settings") or metadata.get("planned_model_settings"),
                "raw_output_sha256": metadata["raw_output_sha256"],
            }
        )
        changed.append(run_id)

    save_json(FORMAL, data)
    print(json.dumps({"updated": changed}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
