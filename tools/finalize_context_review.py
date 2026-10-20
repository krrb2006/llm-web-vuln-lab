#!/usr/bin/env python3
"""Finalize A's evidence review for the four context-ablation records."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "experiments" / "bonus_runs.plan.json"


TARGETS = {
    "CTX_S007_ENTRY": ROOT / "experiments/context_ablation/prepared_sqliv2_rerun/CTX_S007_ENTRY",
    "CTX_S007_FULL": ROOT / "experiments/context_ablation/prepared_sqliv2_rerun/CTX_S007_FULL",
    "CTX_S020_ENTRY": ROOT / "experiments/context_ablation/runs/CTX_S020_ENTRY",
    "CTX_S020_FULL": ROOT / "experiments/context_ablation/runs/CTX_S020_FULL",
}
EXPECTED_TYPE = {"S007": "SQL注入", "S020": "XSS"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    found = set()
    for item in plan:
        run_id = item.get("run_id")
        if run_id not in TARGETS:
            continue
        found.add(run_id)
        run_dir = TARGETS[run_id]
        required = ["input.txt", "metadata.json", "normalized.json", "raw_output.txt"]
        for name in required:
            if not (run_dir / name).is_file():
                raise SystemExit(f"{run_id}: missing {name}")
        metadata = json.loads((run_dir / "metadata.json").read_text(encoding="utf-8"))
        normalized = json.loads((run_dir / "normalized.json").read_text(encoding="utf-8"))
        sample_id = metadata["sample_id"]
        if normalized.get("format_valid") is not True:
            raise SystemExit(f"{run_id}: format_valid is not true")
        parsed = normalized.get("parsed_json") or {}
        if parsed.get("sample_id") != sample_id:
            raise SystemExit(f"{run_id}: sample_id mismatch")
        if parsed.get("vulnerability_type") != EXPECTED_TYPE[sample_id]:
            raise SystemExit(f"{run_id}: vulnerability_type mismatch")
        if sha256(run_dir / "input.txt") != metadata.get("input_sha256"):
            raise SystemExit(f"{run_id}: input hash mismatch")
        if sha256(run_dir / "raw_output.txt") != metadata.get("raw_output_sha256"):
            raise SystemExit(f"{run_id}: raw output hash mismatch")
        if normalized.get("human_verification") != "pending":
            raise SystemExit(f"{run_id}: human_verification must remain pending")
        item["status"] = "reviewed"
        item["reviewer"] = "A"
        item["evidence_paths"] = [
            str((run_dir / name).relative_to(ROOT)).replace("\\", "/")
            for name in required
        ]
    if found != set(TARGETS):
        raise SystemExit(f"missing plan entries: {sorted(set(TARGETS) - found)}")
    PLAN.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"reviewed": sorted(found)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
