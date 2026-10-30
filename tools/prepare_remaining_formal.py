"""Prepare the remaining A/C formal inputs without changing formal results."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = {"S007", "S009", "S012", "S020", "S021", "S023"}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n")


def main() -> None:
    plan = json.loads((ROOT / "runs" / "formal.json").read_text(encoding="utf-8"))
    for row in plan:
        sid = row["sample_id"]
        if sid not in TARGETS:
            continue
        version = row["prompt_version"]
        run_id = row["run_id"]
        kind = "SQLi" if int(sid[1:]) <= 12 else "XSS"
        packet = ROOT / "dataset" / "packets" / f"{sid}_v2" / "code_input.txt"
        if not packet.exists():
            packet = ROOT / "dataset" / "packets" / f"{sid}_v1" / "code_input.txt"
        prompt = ROOT / "prompts" / f"{kind}_{version}.txt"
        code = canonical(packet)
        data = prompt.read_bytes().replace(b"\r\n", b"\n").rstrip(b"\n") + b"\n\n" + code
        out = ROOT / "runs" / run_id
        out.mkdir(parents=True, exist_ok=True)
        meta_path = out / "metadata.json"
        if meta_path.exists():
            existing = json.loads(meta_path.read_text(encoding="utf-8"))
            if existing.get("input_sha256") != sha(data):
                raise RuntimeError(f"existing input differs: {run_id}")
            continue
        meta = {
            "run_id": run_id,
            "phase": "F",
            "sample_id": sid,
            "variant": "Original",
            "prompt_version": version,
            "vulnerability_type": kind,
            "status": "input_prepared",
            "model_display_name": None,
            "model_settings": None,
            "submitted_at": None,
            "prompt_sha256": sha(prompt.read_bytes().replace(b"\r\n", b"\n")),
            "packet_sha256": sha(code),
            "input_sha256": sha(data),
            "raw_output_sha256": None,
            "source_code_input": str(packet.resolve()),
            "planned_model_display_name": "DeepSeek-V4.1-Flash",
            "planned_model_settings": "深度思考=开；联网搜索=关",
            "raw_source": "DeepSeek web session",
            "submission_mode": "A authorized browser automation",
        }
        (out / "input.txt").write_bytes(data)
        meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(run_id)


if __name__ == "__main__":
    main()
