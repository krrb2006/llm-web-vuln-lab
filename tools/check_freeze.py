"""Audit whether the experiment is ready for formal runs.

This tool is deliberately read-only. It validates project structure, review
metadata and hashes, but it never calls an LLM or executes a POC.
"""

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


VERSIONS = ("V0", "V1", "V2")
MEMBERS = {"A", "B", "C", "D"}
EXPECTED_IDS = {f"S{number:03d}" for number in range(1, 25)}
EXPECTED_TEST_IDS = {
    *(f"S{number:03d}" for number in range(7, 13)),
    *(f"S{number:03d}" for number in range(19, 25)),
}
REVIEWER_BY_OPERATOR = {"A": "D", "B": "A", "C": "B", "D": "C"}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _inside_file(root, value):
    if not isinstance(value, str) or not value.strip():
        return None
    path = (root / value).resolve()
    return path if path.is_relative_to(root) and path.is_file() else None


def audit(manifest, runs, root, prompts_dir="prompts", packets_dir="dataset/packets"):
    """Return a deterministic, JSON-serializable freeze-readiness report."""
    root = Path(root).resolve()
    blockers = []
    warnings = [
        {
            "code": "MANUAL_GATES_NOT_AUTOMATED",
            "message": (
                "仍需人工确认冻结单四人签字、统一运行环境/数据库状态、"
                "普通请求与参考验证可运行。"
            ),
        }
    ]

    def block(code, message, subject=None):
        item = {"code": code, "message": message}
        if subject:
            item["subject"] = subject
        blockers.append(item)

    if not isinstance(manifest, list):
        block("MANIFEST_NOT_LIST", "manifest 顶层必须是数组")
        manifest = []
    if not isinstance(runs, list):
        block("RUNS_NOT_LIST", "runs 顶层必须是数组")
        runs = []

    ids = [item.get("sample_id") for item in manifest if isinstance(item, dict)]
    duplicate_ids = sorted(
        (sid for sid, count in Counter(ids).items() if count > 1), key=str
    )
    if duplicate_ids:
        block("DUPLICATE_SAMPLE_ID", f"样本编号重复：{', '.join(duplicate_ids)}")
    actual_ids = {sid for sid in ids if isinstance(sid, str)}
    if actual_ids != EXPECTED_IDS:
        missing = sorted(EXPECTED_IDS - actual_ids)
        extra = sorted(actual_ids - EXPECTED_IDS)
        block("SAMPLE_SET_MISMATCH", f"样本集合不符；缺失={missing}，多余={extra}")

    samples = {
        item["sample_id"]: item
        for item in manifest
        if isinstance(item, dict) and isinstance(item.get("sample_id"), str)
    }
    actual_test_ids = {
        sid for sid, item in samples.items() if item.get("split") == "test"
    }
    if actual_test_ids != EXPECTED_TEST_IDS:
        block(
            "TEST_SET_MISMATCH",
            f"正式测试集不符；缺失={sorted(EXPECTED_TEST_IDS-actual_test_ids)}，"
            f"多余={sorted(actual_test_ids-EXPECTED_TEST_IDS)}",
        )

    families = defaultdict(list)
    for sid, sample in sorted(samples.items()):
        families[sample.get("family_id")].append(sample)
        if sample.get("split") not in {"dev", "test"}:
            block("INVALID_SPLIT", "split 必须为 dev 或 test", sid)
        if sample.get("construction_target") not in {"vulnerable", "fixed"}:
            block("INVALID_CONSTRUCTION_TARGET", "构造目标必须为 vulnerable 或 fixed", sid)
        if sample.get("vulnerability_type") not in {"SQLi", "XSS"}:
            block("INVALID_VULNERABILITY_TYPE", "漏洞类型必须为 SQLi 或 XSS", sid)
        if type(sample.get("ground_truth")) is not bool:
            block("GROUND_TRUTH_NOT_REVIEWED", "ground_truth 尚未完成双人复核", sid)
        reviewer = sample.get("truth_reviewer")
        if reviewer not in MEMBERS or reviewer == sample.get("creator"):
            block("INVALID_TRUTH_REVIEWER", "真值复核人缺失、无效或与创建人相同", sid)
        if sample.get("status") != "ready":
            block("SAMPLE_NOT_READY", "status 必须为 ready", sid)
        digest = sample.get("case_code_sha256")
        if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest):
            block("INVALID_CODE_SHA256", "case_code_sha256 必须是 64 位小写 SHA-256", sid)
        evidence = sample.get("truth_evidence")
        if not isinstance(evidence, list) or not evidence:
            block("MISSING_TRUTH_EVIDENCE", "truth_evidence 必须是非空路径数组", sid)
        else:
            for value in evidence:
                if _inside_file(root, value) is None:
                    block("INVALID_TRUTH_EVIDENCE", f"真值证据不存在或越出仓库：{value}", sid)

    for family, members in sorted(families.items(), key=lambda item: str(item[0])):
        targets = {member.get("construction_target") for member in members}
        splits = {member.get("split") for member in members}
        types = {member.get("vulnerability_type") for member in members}
        if len(members) != 2 or targets != {"vulnerable", "fixed"} or len(splits) != 1 or len(types) != 1:
            block(
                "INVALID_FAMILY_PAIR",
                "每个家族必须恰有同类型、同 split 的 vulnerable/fixed 两例",
                str(family),
            )

    expected_keys = {(sid, version) for sid in EXPECTED_TEST_IDS for version in VERSIONS}
    observed = {}
    run_ids = Counter()
    for run in runs:
        if not isinstance(run, dict):
            block("INVALID_RUN_RECORD", "运行记录必须是对象")
            continue
        sid = run.get("sample_id")
        version = run.get("prompt_version")
        key = (sid, version)
        run_id = run.get("run_id")
        if isinstance(run_id, str):
            run_ids[run_id] += 1
        if key not in expected_keys:
            block("UNEXPECTED_FORMAL_RUN", f"不在 36 条正式计划内：{key}", str(run_id))
            continue
        if key in observed:
            block("DUPLICATE_FORMAL_RUN", f"样本/Prompt 组合重复：{key}", str(run_id))
            continue
        observed[key] = run
        expected_run_id = f"F_{sid}_{version}_R1"
        if run_id != expected_run_id:
            block("INVALID_RUN_ID", f"run_id 应为 {expected_run_id}", str(run_id))
        if run.get("phase") != "formal":
            block("INVALID_RUN_PHASE", "主实验 phase 必须为 formal", expected_run_id)
        if run.get("status") not in {"planned", "reviewed"}:
            block("INVALID_RUN_STATUS", "冻结时状态只能为 planned 或 reviewed", expected_run_id)
        sample = samples.get(sid, {})
        operator = run.get("operator")
        reviewer = run.get("reviewer")
        if operator != sample.get("owner"):
            block("OPERATOR_MISMATCH", "operator 与 manifest.owner 不一致", expected_run_id)
        if reviewer != REVIEWER_BY_OPERATOR.get(operator):
            block("REVIEWER_MISMATCH", "reviewer 与冻结交换复核规则不一致", expected_run_id)
        if not str(run.get("model_display_name", "")).strip():
            block("MODEL_NOT_LOCKED", "model_display_name 尚未冻结", expected_run_id)
        for field, code in (
            ("packet_sha256", "INVALID_PACKET_SHA256"),
            ("prompt_sha256", "INVALID_PROMPT_SHA256"),
        ):
            digest = run.get(field)
            if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest):
                block(code, f"{field} 必须是 64 位小写 SHA-256", expected_run_id)

    duplicate_run_ids = sorted(run_id for run_id, count in run_ids.items() if count > 1)
    if duplicate_run_ids:
        block("DUPLICATE_RUN_ID", f"run_id 重复：{', '.join(duplicate_run_ids)}")
    missing_keys = sorted(expected_keys - set(observed))
    if missing_keys:
        block("MISSING_FORMAL_RUNS", f"缺少 {len(missing_keys)} 条正式计划：{missing_keys}")

    prompt_hashes = {}
    prompt_root = (root / prompts_dir).resolve()
    for vuln_type in ("SQLi", "XSS"):
        for version in VERSIONS:
            name = f"{vuln_type}_{version}.txt"
            path = (prompt_root / name).resolve()
            if not path.is_relative_to(root) or not path.is_file():
                block("MISSING_PROMPT_FILE", f"缺少冻结 Prompt：{Path(prompts_dir) / name}")
                continue
            if not path.read_text(encoding="utf-8-sig").strip():
                block("EMPTY_PROMPT_FILE", f"冻结 Prompt 为空：{Path(prompts_dir) / name}")
                continue
            prompt_hashes[(vuln_type, version)] = sha256_file(path)

    for key, run in sorted(observed.items()):
        sid, version = key
        vuln_type = samples.get(sid, {}).get("vulnerability_type")
        expected_hash = prompt_hashes.get((vuln_type, version))
        actual_hash = run.get("prompt_sha256")
        if expected_hash and SHA256_RE.fullmatch(str(actual_hash or "")) and actual_hash != expected_hash:
            block("PROMPT_HASH_MISMATCH", "记录哈希与冻结 Prompt 文件不一致", run.get("run_id"))

    packet_root = (root / packets_dir).resolve()
    packet_index = defaultdict(list)
    if packet_root.is_relative_to(root) and packet_root.is_dir():
        for path in packet_root.glob("**/code_input.txt"):
            resolved = path.resolve()
            if resolved.is_relative_to(root) and resolved.is_file():
                packet_index[sha256_file(resolved)].append(resolved)
    if not packet_index:
        block("NO_PACKET_FILES", f"{packets_dir} 下没有可验收的 code_input.txt")
    for sid in sorted(EXPECTED_TEST_IDS):
        sample_runs = [observed[(sid, version)] for version in VERSIONS if (sid, version) in observed]
        hashes = {
            run.get("packet_sha256")
            for run in sample_runs
            if SHA256_RE.fullmatch(str(run.get("packet_sha256") or ""))
        }
        if len(hashes) > 1:
            block("PACKET_HASH_NOT_STABLE", "同一样本的三版 Prompt 必须使用同一输入包", sid)
        for digest in hashes:
            matches = packet_index.get(digest, [])
            if not matches:
                block("PACKET_HASH_NOT_FOUND", "仓库内没有与记录哈希匹配的 code_input.txt", sid)
                continue
            matching_sid = []
            for path in matches:
                text = path.read_text(encoding="utf-8-sig")
                if f"<sample_id>{sid}</sample_id>" in text:
                    matching_sid.append(path)
            if len(matching_sid) != 1:
                block("PACKET_ID_AMBIGUOUS", "输入包哈希未唯一对应当前 sample_id", sid)
                continue
            line_map = matching_sid[0].with_name("line_map.json")
            if not line_map.is_file():
                block("MISSING_LINE_MAP", f"输入包缺少 line_map.json：{matching_sid[0].parent}", sid)
                continue
            try:
                mapping = json.loads(line_map.read_text(encoding="utf-8-sig"))
            except (OSError, json.JSONDecodeError):
                block("INVALID_LINE_MAP", f"line_map.json 无法解析：{line_map}", sid)
                continue
            if not isinstance(mapping, dict):
                block("INVALID_LINE_MAP", f"line_map.json 顶层必须是对象：{line_map}", sid)
                continue
            if mapping.get("sample_id") != sid or mapping.get("packet_sha256") != digest:
                block("LINE_MAP_MISMATCH", "line_map 的 sample_id 或 packet_sha256 不一致", sid)

    models = {
        str(run.get("model_display_name", "")).strip()
        for run in observed.values()
        if str(run.get("model_display_name", "")).strip()
    }
    if len(models) > 1:
        block("MULTIPLE_MODELS", f"主实验必须冻结同一模型，当前为：{sorted(models)}")

    counts = Counter(item["code"] for item in blockers)
    return {
        "ready": not blockers,
        "summary": {
            "manifest_records": len(manifest),
            "test_samples": len(actual_test_ids),
            "formal_plan_records": len(observed),
            "prompt_files_found": len(prompt_hashes),
            "packet_files_indexed": sum(len(paths) for paths in packet_index.values()),
            "blockers": len(blockers),
        },
        "artifacts": {
            "prompt_sha256": {
                f"{vuln_type}_{version}": digest
                for (vuln_type, version), digest in sorted(prompt_hashes.items())
            }
        },
        "blocker_counts": dict(sorted(counts.items())),
        "blockers": blockers,
        "warnings": warnings,
    }


def render_markdown(report):
    status = "READY" if report["ready"] else "BLOCKED"
    summary = report["summary"]
    lines = [
        "# 正式测试冻结自动验收",
        "",
        f"结论：**{status}**",
        "",
        "|检查项|数量|",
        "|---|---:|",
        f"|manifest 记录|{summary['manifest_records']}|",
        f"|正式样本|{summary['test_samples']}|",
        f"|正式计划记录|{summary['formal_plan_records']}|",
        f"|可读 Prompt 文件|{summary['prompt_files_found']}|",
        f"|已索引输入包|{summary['packet_files_indexed']}|",
        f"|阻塞项|{summary['blockers']}|",
        "",
        "## 当前 Prompt SHA-256",
        "",
        "|Prompt|SHA-256|",
        "|---|---|",
    ]
    for name, digest in report["artifacts"]["prompt_sha256"].items():
        lines.append(f"|{name}|`{digest}`|")
    lines.extend([
        "",
        "## 阻塞项",
        "",
    ])
    if report["blockers"]:
        grouped = defaultdict(list)
        messages = {}
        for item in report["blockers"]:
            messages.setdefault(item["code"], item["message"])
            if item.get("subject"):
                grouped[item["code"]].append(item["subject"])
        lines.extend(["|代码|数量|对象|说明|", "|---|---:|---|---|"])
        for code, count in report["blocker_counts"].items():
            subjects = sorted(set(grouped[code]))
            subject_text = "、".join(subjects[:12])
            if len(subjects) > 12:
                subject_text += f" 等 {len(subjects)} 项"
            lines.append(f"|`{code}`|{count}|{subject_text}|{messages[code]}|")
    else:
        lines.append("- 自动检查通过。")
    lines.extend(["", "## 人工关口", ""])
    for item in report["warnings"]:
        lines.append(f"- `{item['code']}`：{item['message']}")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default="dataset/manifest.json")
    parser.add_argument("--runs", default="runs/formal.json")
    parser.add_argument("--root", default=".")
    parser.add_argument("--prompts-dir", default="prompts")
    parser.add_argument("--packets-dir", default="dataset/packets")
    parser.add_argument("--json-out")
    parser.add_argument("--md-out")
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="always exit 0; useful while resolving blockers",
    )
    args = parser.parse_args()
    read_json = lambda path: json.loads(Path(path).read_text(encoding="utf-8-sig"))
    report = audit(
        read_json(args.manifest),
        read_json(args.runs),
        args.root,
        args.prompts_dir,
        args.packets_dir,
    )
    if args.json_out:
        Path(args.json_out).write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    markdown = render_markdown(report)
    if args.md_out:
        Path(args.md_out).write_text(markdown, encoding="utf-8")
    print(markdown, end="")
    if not report["ready"] and not args.report_only:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
