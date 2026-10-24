"""Derive and lock immutable metadata for the 36 formal experiment runs.

The command is read-only unless ``--write`` is supplied.  It deliberately
refuses to produce a lock while any truth review, packet, prompt, or provenance
check is incomplete.  It never calls a model and never fills result fields.
"""

import argparse
import copy
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.check_freeze import EXPECTED_TEST_IDS, VERSIONS, audit, sha256_lf_text


def _load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def _truth_gate(manifest, root):
    failures = []
    for sample in manifest:
        sid = sample.get("sample_id", "<unknown>")
        if type(sample.get("ground_truth")) is not bool:
            failures.append(f"{sid}: ground_truth 尚未复核")
        reviewer = sample.get("truth_reviewer")
        if reviewer not in {"A", "B", "C", "D"} or reviewer == sample.get("creator"):
            failures.append(f"{sid}: truth_reviewer 缺失、无效或与 creator 相同")
        if sample.get("status") != "ready":
            failures.append(f"{sid}: status 不是 ready")
        evidence = sample.get("truth_evidence")
        if not isinstance(evidence, list) or not evidence:
            failures.append(f"{sid}: truth_evidence 为空")
            continue
        for relative in evidence:
            path = (root / relative).resolve() if isinstance(relative, str) else None
            if path is None or not path.is_relative_to(root) or not path.is_file():
                failures.append(f"{sid}: 真值证据不存在或越出仓库：{relative}")
    if failures:
        preview = "\n".join(f"- {item}" for item in failures[:20])
        suffix = f"\n- 另有 {len(failures) - 20} 项" if len(failures) > 20 else ""
        raise ValueError(f"真值门禁未通过，禁止锁定正式计划：\n{preview}{suffix}")


def _packet_hashes(root):
    by_sample = {}
    packet_root = root / "dataset" / "packets"
    for path in packet_root.glob("**/code_input.txt"):
        mapping_path = path.with_name("line_map.json")
        if not mapping_path.is_file():
            continue
        mapping = _load_json(mapping_path)
        sid = mapping.get("sample_id")
        if sid not in EXPECTED_TEST_IDS:
            continue
        digest = sha256_lf_text(path)
        if mapping.get("packet_sha256") != digest:
            raise ValueError(f"{sid}: line_map 与输入包哈希不一致：{path}")
        by_sample.setdefault(sid, []).append((path, digest))
    result = {}
    for sid in sorted(EXPECTED_TEST_IDS):
        matches = by_sample.get(sid, [])
        if len(matches) != 1:
            raise ValueError(f"{sid}: 应唯一对应一个正式输入包，实际为 {len(matches)} 个")
        result[sid] = matches[0][1]
    return result


def build_locked_runs(manifest, runs, root, model_display_name, model_settings):
    """Return a validated locked copy without mutating ``runs``."""
    root = Path(root).resolve()
    model_display_name = model_display_name.strip()
    model_settings = model_settings.strip()
    if not model_display_name or not model_settings:
        raise ValueError("模型显示名称和模型设置均不能为空")
    _truth_gate(manifest, root)

    samples = {item["sample_id"]: item for item in manifest}
    packets = _packet_hashes(root)
    prompt_hashes = {
        (kind, version): sha256_lf_text(root / "prompts" / f"{kind}_{version}.txt")
        for kind in ("SQLi", "XSS")
        for version in VERSIONS
    }
    locked = copy.deepcopy(runs)
    expected = {(sid, version) for sid in EXPECTED_TEST_IDS for version in VERSIONS}
    observed = {(item.get("sample_id"), item.get("prompt_version")) for item in locked}
    if observed != expected or len(locked) != len(expected):
        raise ValueError("runs/formal.json 必须恰好包含 12×3 条唯一正式计划")

    for run in locked:
        sid = run["sample_id"]
        version = run["prompt_version"]
        kind = samples[sid]["vulnerability_type"]
        run["model_display_name"] = model_display_name
        run["model_settings"] = model_settings
        run["packet_sha256"] = packets[sid]
        run["prompt_sha256"] = prompt_hashes[(kind, version)]

    report = audit(manifest, locked, root)
    if not report["ready"]:
        summary = "; ".join(
            f"{item['code']}:{item.get('subject', '-')}" for item in report["blockers"][:12]
        )
        raise ValueError(f"完整冻结验收未通过：{summary}")
    return locked


def _atomic_write_json(path, value):
    path = Path(path)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default="dataset/manifest.json")
    parser.add_argument("--runs", default="runs/formal.json")
    parser.add_argument("--model-display-name", required=True)
    parser.add_argument("--model-settings", required=True)
    parser.add_argument("--write", action="store_true", help="通过全部门禁后原子更新 runs 文件")
    args = parser.parse_args()

    manifest_path = (ROOT / args.manifest).resolve()
    runs_path = (ROOT / args.runs).resolve()
    for path in (manifest_path, runs_path):
        if not path.is_relative_to(ROOT):
            raise SystemExit(f"路径越出仓库：{path}")
    try:
        locked = build_locked_runs(
            _load_json(manifest_path),
            _load_json(runs_path),
            ROOT,
            args.model_display_name,
            args.model_settings,
        )
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        raise SystemExit(f"BLOCKED: {exc}") from None
    if args.write:
        _atomic_write_json(runs_path, locked)
        print(f"LOCKED: {len(locked)} records written to {runs_path.relative_to(ROOT)}")
    else:
        print(f"DRY RUN READY: {len(locked)} records; add --write only after four-person sign-off")


if __name__ == "__main__":
    main()
