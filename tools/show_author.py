"""Print the responsible author for a repository path.

作者：A 刘珂如
职责：为教师根据报错路径反查代码作者提供统一入口。
"""

from __future__ import annotations

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


RULES = (
    ("tools/", "A 刘珂如", "冻结检查、审计、指标评估和项目工具", "docs/A_判定评估与整合操作手册.md"),
    ("tests/", "A 刘珂如", "项目验收测试和质量检查", "docs/A_判定评估与整合操作手册.md"),
    ("dataset/", "C 常佳佳", "样本源码、预处理、真值输入和行号映射", "docs/C_样本与预处理操作手册.md"),
    ("submission_inputs/", "C 常佳佳", "模型提交输入包", "docs/C_样本与预处理操作手册.md"),
    ("prompts/", "B 张思佳", "SQLi/XSS Prompt 和版本迭代", "docs/B_Prompt与模型对照操作手册.md"),
    ("environment/", "D 李楠", "Docker/DVWA 环境和运行检查", "docs/D_环境与POC验证操作手册.md"),
    ("pocs/", "D 李楠", "POC 验证脚本", "docs/D_环境与POC验证操作手册.md"),
    ("demo/", "D 李楠", "Burp 联动和演示证据", "docs/D_环境与POC验证操作手册.md"),
    ("evidence/", "D 李楠", "请求、响应、截图和验证证据", "docs/D_环境与POC验证操作手册.md"),
    ("docs/A_", "A 刘珂如", "判定、真值、复核、统计和阶段整合", "docs/A_判定评估与整合操作手册.md"),
    ("docs/B_", "B 张思佳", "Prompt 实验、模型记录和迭代分析", "docs/B_Prompt与模型对照操作手册.md"),
    ("docs/C_", "C 常佳佳", "样本审核、输入包和独立复核", "docs/C_样本与预处理操作手册.md"),
    ("docs/D_", "D 李楠", "环境、POC、Burp 和运行复核", "docs/D_环境与POC验证操作手册.md"),
    ("docs/最终", "A 刘珂如", "全组最终报告整合", "docs/代码说明_教师测试指南.md"),
    ("docs/网络安全大作业实验报告", "A 刘珂如", "全组最终报告整合", "docs/代码说明_教师测试指南.md"),
    ("results/A_", "A 刘珂如", "判定、真值、复核、统计和阶段整合", "docs/A_判定评估与整合操作手册.md"),
    ("results/B_", "B 张思佳", "Prompt 实验、模型记录和迭代分析", "docs/B_Prompt与模型对照操作手册.md"),
    ("results/C_", "C 常佳佳", "样本审核、输入包和独立复核", "docs/C_样本与预处理操作手册.md"),
    ("results/D_", "D 李楠", "环境、POC、Burp 和运行复核", "docs/D_环境与POC验证操作手册.md"),
)


def normalize(value: str) -> str:
    path = Path(value)
    try:
        relative = path.resolve().relative_to(ROOT)
    except ValueError:
        relative = Path(value)
    return relative.as_posix().lstrip("./")


def find_author(relative: str):
    for prefix, author, responsibility, guide in RULES:
        if relative == prefix.rstrip("/") or relative.startswith(prefix):
            return author, responsibility, guide
    if relative.startswith(("experiments/", "runs/", "templates/")):
        return "全组协作", "加分实验、模型运行归档或共同模板", "AUTHORS.md"
    return "A 刘珂如（最终整合）", "共同文件或未单独归类文件的最终维护与整合", "AUTHORS.md"


def main() -> int:
    parser = argparse.ArgumentParser(description="根据报错文件路径查询代码作者")
    parser.add_argument("path", help="仓库内文件路径")
    args = parser.parse_args()
    relative = normalize(args.path)
    author, responsibility, guide = find_author(relative)
    print(f"文件: {relative}")
    print(f"作者: {author}")
    print(f"职责: {responsibility}")
    print(f"说明: {guide}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
