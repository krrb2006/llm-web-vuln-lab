#!/usr/bin/env python3
"""Mark captured context-ablation entries as executed, not reviewed."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "experiments" / "bonus_runs.plan.json"


def main() -> int:
    data = json.loads(PLAN.read_text(encoding="utf-8"))
    target = {
        # The original S007 records are preserved as a mismatched XSS_V2
        # observation. The plan points to the corrected SQLi_V2 rerun.
        "CTX_S007_ENTRY": "experiments/context_ablation/prepared_sqliv2_rerun/CTX_S007_ENTRY",
        "CTX_S007_FULL": "experiments/context_ablation/prepared_sqliv2_rerun/CTX_S007_FULL",
        "CTX_S020_ENTRY": "experiments/context_ablation/runs/CTX_S020_ENTRY",
        "CTX_S020_FULL": "experiments/context_ablation/runs/CTX_S020_FULL",
    }
    changed = []
    for item in data:
        run_id = item.get("run_id")
        if run_id not in target:
            continue
        run_dir = ROOT / target[run_id]
        for filename in ("input.txt", "metadata.json", "normalized.json", "raw_output.txt"):
            if not (run_dir / filename).is_file():
                raise SystemExit(f"{run_id}: missing {filename}")
        item["status"] = "executed"
        item["evidence_paths"] = [
            f"{target[run_id]}/input.txt",
            f"{target[run_id]}/metadata.json",
            f"{target[run_id]}/normalized.json",
            f"{target[run_id]}/raw_output.txt",
        ]
        changed.append(run_id)
    PLAN.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"updated": changed}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
