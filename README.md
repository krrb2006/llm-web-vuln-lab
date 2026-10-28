# LLM 辅助 Web 漏洞挖掘与验证

网络安全课程四人小组实验：面向 SQL 注入和 XSS 的提示词迭代及误漏报分析。

**当前状态：项目已完成。24 个教学样本、12 个正式样本、36 条正式记录（36/36 reviewed）、26 条加分证据（26/26 reviewed）、22/22 单元测试、冻结检查 READY、严格提交审计 READY。**

- 正式结果：V0/V1/V2 各 12 条，TP=6、FP=0、TN=6、FN=0，判定与定位准确率 100%。
- 加分实验：Prompt Injection 16、Burp 联动 2、CTX 4、ADV 4。
- 模型口径：DeepSeek 网页默认/快速模式；按官方 2026-10-17 公告映射为 `V4.1-Flash-1017`；单次 API/HAR 的 `model` 字段未捕获。
- 复核口径：S001 8 条为 A 项目内自审，C 明确不把独立签字作为提交阻塞项；ADV 的 POC 标记 `not_run`，不冒充已触发。

## 最终交付物

- [完整版实验报告](docs/实验报告_完整版_2026-10-27.docx)
- [比赛答辩 PPT](docs/答辩PPT_比赛答辩版_2026-10-27.pptx)
- [口头报告执行文档（4人×1分钟 / 12页PPT脚本）](docs/口头报告_4人分工与12页PPT脚本_2026-10-28.docx)
- [Q&A 收尾页（单页，插在第12页结论之后）](docs/PPT_收尾页_Q&A_2026-10-28.pptx)
- [12页PPT逐页详细内容与截图（最终版）](docs/口头报告_12页PPT逐页详细内容与截图_最终版_2026-10-28.docx)
- [正式统计结果](results/formal_eval_2026-10-19-v2/summary.md)
- [模型口径说明](results/A_model_provenance_update_2026-10-26.md)

## 从这里开始

1. 先看[完整版实验报告](docs/实验报告_完整版_2026-10-27.docx)和[比赛答辩 PPT](docs/答辩PPT_比赛答辩版_2026-10-27.pptx)，了解实验设计与结论。
2. 看[正式统计](results/formal_eval_2026-10-19-v2/summary.md)与 `runs/formal.json`，核对 36 条正式记录。
3. 按 [D 环境手册](docs/D_环境与POC验证操作手册.md) 与 `environment/` 复现 Docker/DVWA 靶场。
4. 运行 `check_freeze.py`、`audit_submission.py` 和单元测试复核最终状态。

|成员|职责|操作文档|正式样本|记录数|
|---|---|---|---|---|
|A|判定、真值、指标与整合|[A 手册](docs/A_判定评估与整合操作手册.md)|S007、S020、S021|9|
|B|Prompt、迭代与模型对照|[B 手册](docs/B_Prompt与模型对照操作手册.md)|S008、S019、S024|9|
|C|样本、预处理与追溯|[C 手册](docs/C_样本与预处理操作手册.md)|S009、S012、S023|9|
|D|环境、POC、Burp 与第二台电脑复现|[D 手册](docs/D_环境与POC验证操作手册.md)|S010、S011、S022|9|

## 目录

|目录|内容|
|---|---|
|docs/|总手册及 A/B/C/D 手册，Markdown 和 Word 版本|
|prompts/|SQLi、XSS 各 V0/V1/V2；六份冻结 Prompt|
|templates/|记录、审核、冻结、演示模板与计划清单|
|dataset/|样本、编号输入、映射及 manifest.json|
|runs/|formal.json 和后续原始模型记录|
|pocs/、evidence/|验证代码、脱敏日志与截图|
|results/、demo/|实际统计结果、演示材料|
|environment/|版本信息、部署说明|
|tools/|标准库辅助脚本：输入编号、记录校验与评估|
|experiments/|Prompt 注入、Burp 联动、上下文消融、二次注入与逻辑漏洞加分实验|

`dataset/manifest.json` 记录 24 个样本；`runs/formal.json` 记录 36 条已复核的正式运行，36/36 为 `reviewed`；加分计划见 `experiments/bonus_runs.plan.json`。

## 本地开始

从 GitHub 克隆本仓库后进入目录，使用 Python 3 查看脚本参数：

```bash
python3 tools/prepare_input.py --help
python3 tools/check_freeze.py --report-only
python3 tools/freeze_plan.py --help
python3 tools/audit_submission.py
python3 tools/evaluate.py --help
python3 tools/build_evidence_index.py --help
python3 -m unittest discover -s tests -v
```

`check_freeze.py` 在正式测试前只读检查 24 例真值与证据、36 条运行计划、
执行/复核分工，以及源码、输入包、Prompt 哈希和 line_map 源文件/行范围。文本哈希
统一按 UTF-8/LF 计算，避免 Windows 与 Linux 换行差异。只有自动检查为 `READY`，并完成
冻结单列出的环境验证与四人签字后，才能开始正式测试；`--report-only` 用于在
准备阶段查看全部阻塞项而不返回失败退出码。

环境部署按 D 手册进行。辅助脚本不部署靶场、不调用模型、不执行 POC。手册中的 `~/llm-web-lab` 可替换为你自己的仓库路径；已有克隆仓库不需要再运行 `git init`。

## 协作

见 [协作规范](CONTRIBUTING.md) 和 [启动任务](docs/启动任务.md)。每人使用独立分支，以 Pull Request 提交自己的成果并交叉复核。当前 Markdown 文档为协作编辑版；Word 是初始化快照，修改后应统一重新导出。

所有验证仅用于授权的本地教学靶场；证据提交前去除登录 Cookie、令牌与个人信息。第三方源码保留来源、提交号和原许可证；本仓库暂未授予统一开源许可证。
