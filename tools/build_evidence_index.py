"""Build a report-ready traceability index from reviewed and planned records."""
import argparse
import json
from pathlib import Path


def _read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def _format_paths(paths):
    if not paths:
        return "—"
    return "<br>".join(f"`{item}`" for item in paths)


def build_index(manifest, formal, bonus):
    truth_by_id = {item["sample_id"]: item for item in manifest}
    lines = [
        "# 实验结论到原始证据索引",
        "",
        "本表由记录文件生成，只显示状态和路径，不判断证据内容是否充分。`planned` 不能作为实测结论。",
        "",
        "## 正式实验",
        "",
        "|run_id|样本|版本|状态|预测|真值状态|模型与POC证据|",
        "|---|---|---|---|---|---|---|",
    ]
    for run in formal:
        sample = truth_by_id.get(run.get("sample_id"), {})
        truth = sample.get("ground_truth")
        truth_status = "未复核" if type(truth) is not bool else ("有漏洞" if truth else "安全")
        lines.append(
            f"|`{run.get('run_id', '')}`|{run.get('sample_id', '')}|"
            f"{run.get('prompt_version', '')}|{run.get('status', '')}|"
            f"{run.get('prediction') or '—'}|{truth_status}|"
            f"{_format_paths(run.get('evidence_paths', []))}|"
        )
    lines.extend([
        "",
        "## 加分实验",
        "",
        "|run_id|类别|样本|条件|状态|证据|",
        "|---|---|---|---|---|---|",
    ])
    for run in bonus:
        lines.append(
            f"|`{run.get('run_id', '')}`|{run.get('category', '')}|"
            f"{run.get('sample_id', '')}|{run.get('condition', '')}|"
            f"{run.get('status', '')}|{_format_paths(run.get('evidence_paths', []))}|"
        )
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default="dataset/manifest.json")
    parser.add_argument("--formal", default="runs/formal.json")
    parser.add_argument("--bonus", default="experiments/bonus_runs.plan.json")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    output = Path(args.out)
    if output.exists():
        raise ValueError("output exists; choose a new versioned evidence index path")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        build_index(_read(args.manifest), _read(args.formal), _read(args.bonus)),
        encoding="utf-8",
    )
    print(f"Evidence index saved to {output}")


if __name__ == "__main__":
    main()
