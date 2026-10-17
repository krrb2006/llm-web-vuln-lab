"""Audit evidence readiness against the course rubric without inventing results."""
import argparse
import json
from collections import Counter
from pathlib import Path


EXPECTED_BONUS = {
    "prompt_injection": 16,
    "burp_linkage": 2,
    "context_ablation": 4,
    "advanced_case": 4,
}


def _read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def _evidence_complete(root, record):
    paths = record.get("evidence_paths", [])
    return bool(paths) and all(
        (root / item).resolve().is_relative_to(root.resolve())
        and (root / item).is_file()
        for item in paths
    )


def validate_bonus_plan(records):
    issues = []
    ids = [item.get("run_id") for item in records]
    duplicates = sorted(item for item, count in Counter(ids).items() if item and count > 1)
    if duplicates:
        issues.append(f"duplicate bonus run_id: {duplicates}")
    counts = Counter(item.get("category") for item in records)
    for category, expected in EXPECTED_BONUS.items():
        if counts[category] != expected:
            issues.append(
                f"{category} plan count is {counts[category]}, expected {expected}"
            )
    for item in records:
        if item.get("operator") == item.get("reviewer"):
            issues.append(f"{item.get('run_id')}: operator and reviewer must differ")
        if item.get("status") not in {"planned", "executed", "reviewed"}:
            issues.append(f"{item.get('run_id')}: invalid status")
    return issues


def audit_repository(root):
    root = Path(root).resolve()
    manifest = _read_json(root / "dataset" / "manifest.json")
    formal = _read_json(root / "runs" / "formal.json")
    bonus_path = root / "experiments" / "bonus_runs.plan.json"
    bonus = _read_json(bonus_path) if bonus_path.is_file() else []
    bonus_issues = validate_bonus_plan(bonus)

    raw_ids = {
        path.name
        for path in (root / "dataset" / "raw").glob("S[0-9][0-9][0-9]")
        if path.is_dir() and any(path.glob("*.php"))
    }
    packet_ids = {
        path.name.split("_", 1)[0]
        for path in (root / "dataset" / "packets").glob("S[0-9][0-9][0-9]_v*")
        if (path / "code_input.txt").is_file() and (path / "line_map.json").is_file()
    }
    reviewed_truth = sum(
        type(item.get("ground_truth")) is bool
        and bool(item.get("truth_reviewer"))
        and bool(item.get("truth_evidence"))
        for item in manifest
    )
    reviewed_formal = [
        item
        for item in formal
        if item.get("phase") == "formal"
        and item.get("status") == "reviewed"
        and _evidence_complete(root, item)
    ]
    reviewed_bonus = [
        item
        for item in bonus
        if item.get("status") == "reviewed" and _evidence_complete(root, item)
    ]
    prompt_files = [
        root / "prompts" / f"{vulnerability_type}_{version}.txt"
        for vulnerability_type in ("SQLi", "XSS")
        for version in ("V0", "V1", "V2")
    ]
    prompt_ready = sum(path.is_file() and path.stat().st_size > 0 for path in prompt_files)
    result_files = list((root / "results").glob("**/summary.json"))
    final_report_candidates = [
        path for path in (root / "docs").glob("*")
        if path.is_file() and ("最终报告" in path.name or "实验报告" in path.name)
    ]
    advanced_php = list((root / "experiments" / "advanced_cases").glob("**/*.php"))

    checks = [
        {"rubric": "基础", "item": "24例数据集计划", "done": len(manifest), "target": 24},
        {"rubric": "基础", "item": "样本源码落库", "done": len(raw_ids), "target": 24},
        {"rubric": "基础", "item": "标准输入包与行号映射", "done": len(packet_ids), "target": 24},
        {"rubric": "基础", "item": "独立真值复核", "done": reviewed_truth, "target": 24},
        {"rubric": "基础", "item": "六份Prompt文本", "done": prompt_ready, "target": 6},
        {"rubric": "基础", "item": "正式记录计划", "done": len(formal), "target": 36},
        {"rubric": "基础", "item": "正式记录完成且证据可读", "done": len(reviewed_formal), "target": 36},
        {"rubric": "基础", "item": "统计产物", "done": min(len(result_files), 1), "target": 1},
        {"rubric": "基础", "item": "最终实验报告", "done": min(len(final_report_candidates), 1), "target": 1},
        {"rubric": "加分", "item": "加分实验计划结构", "done": 0 if bonus_issues else 1, "target": 1},
        {"rubric": "加分", "item": "加分实验完成且证据可读", "done": len(reviewed_bonus), "target": sum(EXPECTED_BONUS.values())},
        {"rubric": "加分", "item": "二次注入与逻辑漏洞代码蓝图", "done": len(advanced_php), "target": 6},
        {"rubric": "工程", "item": "自动化测试工作流", "done": int((root / ".github" / "workflows" / "quality.yml").is_file()), "target": 1},
    ]
    for item in checks:
        item["status"] = "READY" if item["done"] >= item["target"] else (
            "PARTIAL" if item["done"] else "MISSING"
        )
    return {
        "ready_for_submission": all(
            item["status"] == "READY" for item in checks if item["rubric"] == "基础"
        ),
        "checks": checks,
        "bonus_plan_counts": dict(sorted(Counter(
            item.get("category") for item in bonus
        ).items())),
        "bonus_plan_issues": bonus_issues,
        "notes": [
            "READY only means required files and review states are present; humans must still inspect evidence content.",
            "Planned bonus records never count as completed evidence.",
        ],
    }


def render_markdown(report):
    conclusion = "可提交" if report["ready_for_submission"] else "尚未达到提交门槛"
    lines = [
        "# 课程评分项证据就绪审计",
        "",
        f"结论：**{conclusion}**",
        "",
        "|评分层级|检查项|完成|目标|状态|",
        "|---|---|---:|---:|---|",
    ]
    for item in report["checks"]:
        lines.append(
            f"|{item['rubric']}|{item['item']}|{item['done']}|{item['target']}|{item['status']}|"
        )
    lines.extend(["", "## 加分实验计划", ""])
    for category, target in EXPECTED_BONUS.items():
        actual = report["bonus_plan_counts"].get(category, 0)
        lines.append(f"- `{category}`：{actual}/{target}")
    if report["bonus_plan_issues"]:
        lines.extend(["", "## 计划问题", ""])
        lines.extend(f"- {item}" for item in report["bonus_plan_issues"])
    lines.extend(["", "## 口径说明", ""])
    lines.extend(f"- {item}" for item in report["notes"])
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--json-out")
    parser.add_argument("--md-out")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    report = audit_repository(args.root)
    markdown = render_markdown(report)
    if args.json_out:
        Path(args.json_out).write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    if args.md_out:
        Path(args.md_out).write_text(markdown, encoding="utf-8")
    print(markdown, end="")
    if args.strict and not report["ready_for_submission"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
