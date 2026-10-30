#!/usr/bin/env python3
"""Prepare the four fixed-V2 context-ablation inputs."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMPTS = {
    "S007": ROOT / "prompts" / "SQLi_V2.txt",
    "S020": ROOT / "prompts" / "XSS_V2.txt",
}
FORMAL_RUNS = ROOT / "runs"
ENTRY_ROOT = ROOT / "experiments" / "context_ablation"
OUT_ROOT = ROOT / "experiments" / "context_ablation" / "runs"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_lf(path: Path) -> bytes:
    return path.read_text(encoding="utf-8-sig").replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("sample_id", choices=["S007", "S020"])
    parser.add_argument("condition", choices=["entry_only", "full_context"])
    args = parser.parse_args()

    run_id = f"CTX_{args.sample_id}_{'ENTRY' if args.condition == 'entry_only' else 'FULL'}"
    out = OUT_ROOT / run_id
    out.mkdir(parents=True, exist_ok=True)

    prompt_path = PROMPTS[args.sample_id]
    prompt_bytes = read_lf(prompt_path)
    if args.condition == "entry_only":
        source_dir = ENTRY_ROOT / f"CTX_{args.sample_id}_ENTRY"
        spec = json.loads((source_dir / "spec.json").read_text(encoding="utf-8"))
        runtime = spec["context"]
        code = read_lf(source_dir / "code_input.txt").decode("utf-8")
        packet_bytes = code.encode("utf-8")
        input_text = (
            prompt_bytes.decode("utf-8")
            + "\n\n"
            + "<runtime_context>\n"
            + runtime
            + "\n</runtime_context>\n"
            + "<untrusted_code>\n"
            + code
            + "\n</untrusted_code>\n"
        )
    else:
        source_run = FORMAL_RUNS / f"F_{args.sample_id}_V2_R1"
        packet_bytes = read_lf(source_run / "input.txt")
        input_text = packet_bytes.decode("utf-8")

    input_bytes = input_text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")
    (out / "input.txt").write_bytes(input_bytes)
    metadata = {
        "run_id": run_id,
        "category": "context_ablation",
        "sample_id": args.sample_id,
        "condition": args.condition,
        "prompt_version": "V2",
        "prompt_family": "SQLi" if args.sample_id == "S007" else "XSS",
        "status": "input_prepared",
        "operator": "A (delegated execution for C)",
        "reviewer": "A",
        "model_display_name": None,
        "model_settings": None,
        "submitted_at": None,
        "prompt_sha256": sha256(prompt_bytes),
        "context_sha256": sha256(packet_bytes),
        "input_sha256": sha256(input_bytes),
        "planned_model_display_name": "DeepSeek-V4.1-Flash",
        "planned_model_settings": "深度思考=开；联网搜索=关",
        "raw_source": "DeepSeek web session",
        "submission_mode": "A authorized browser automation",
    }
    (out / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"run_id": run_id, "input_sha256": metadata["input_sha256"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
