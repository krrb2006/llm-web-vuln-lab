# LLM 辅助 Web 漏洞挖掘与验证

网络安全课程四人小组实验：面向 SQL 注入和 XSS 的提示词迭代及误漏报分析。

**当前状态：正式实验 36/36、加分实验 26/26 均已归档并完成项目内复核；自动化测试 22/22 通过。SQLi/XSS 主实验在本组样本上的三版 Prompt 均为 12/12 分类正确、12/12 定位正确，不将该结果外推为真实世界准确率。**

最终交付报告：[Word 版](docs/网络安全大作业实验报告.docx) · [PDF 版](docs/网络安全大作业实验报告.pdf) · [Markdown 源稿](docs/最终实验报告_2026-10-26.md)

## 从这里开始

1. 先阅读 [最终实验报告](docs/最终实验报告_2026-10-26.md) 了解结果与限制，再阅读 [总执行手册](docs/00_总执行手册.md) 和自己的手册。
2. 使用 `dataset/`、`prompts/`、`runs/` 和 `results/` 查看冻结输入、模型记录、复核结论与统计结果。
3. 按 [环境说明](environment/README.md) 启动本地教学靶场，并使用 `tools/` 中的审计和评估脚本复核仓库状态。
4. 需要复现实验时，先运行 `python tools/audit_submission.py` 和测试套件，再按报告附录中的命令检查具体证据。
5. 所有验证仅限授权的本地教学靶场；提交证据前去除登录 Cookie、令牌与个人信息。

|成员|职责|操作文档|正式样本|记录数|
|---|---|---|---|---|
|A|判定、真值、指标与整合|[A 手册](docs/A_判定评估与整合操作手册.md)|S007、S020、S021|9|
|B|Prompt、迭代与模型对照|[B 手册](docs/B_Prompt与模型对照操作手册.md)|S008、S019、S024|9|
|C|样本、预处理与追溯|[C 手册](docs/C_样本与预处理操作手册.md)|S009、S012、S023|9|
|D|环境、POC 与 Burp 联动|[D 手册](docs/D_环境与POC验证操作手册.md)|S010、S011、S022|9|

## 目录

|目录|内容|
|---|---|
|docs/|总手册及 A/B/C/D 手册，Markdown 和 Word 版本|
|prompts/|SQLi、XSS 各 V0/V1/V2；初始候选文本，需真实迭代|
|templates/|记录、审核、冻结、演示模板与计划清单|
|dataset/|样本、编号输入、映射及 manifest.json|
|runs/|formal.json 和后续原始模型记录|
|pocs/、evidence/|验证代码、脱敏日志与截图|
|results/、demo/|实际统计结果、演示材料|
|environment/|版本信息、部署说明|
|tools/|标准库辅助脚本：输入编号、记录校验与评估|
|experiments/|Prompt 注入、Burp 联动、上下文消融、二次注入与逻辑漏洞加分实验|

`dataset/manifest.json` 和 `runs/formal.json` 已从计划模板初始化。未知结果保留 null，不要重复复制覆盖工作记录。

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
