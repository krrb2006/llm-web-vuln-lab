# LLM 辅助 Web 漏洞挖掘与验证

网络安全课程四人小组实验：面向 SQL 注入和 XSS 的提示词迭代及误漏报分析。

**当前状态：项目初始化。尚未完成样本实现、LLM 实验和漏洞验证，没有实测结论。**

## 从这里开始

1. 阅读 [总执行手册](docs/00_总执行手册.md)，再阅读自己的手册。
2. A 确定判定标准，B 准备 V0，C 整理首例源码，D 启动本地靶场。
3. 全组先跑通一例 SQLi 和一例 XSS，再扩展到 24 个样本。
4. 在开发集完成 V0 → V1 → V2 两轮迭代，冻结后完成 36 条正式记录。

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

`dataset/manifest.json` 和 `runs/formal.json` 已从计划模板初始化。未知结果保留 null，不要重复复制覆盖工作记录。

## 本地开始

从 GitHub 克隆本仓库后进入目录，使用 Python 3 查看脚本参数：

```bash
python3 tools/prepare_input.py --help
python3 tools/evaluate.py --help
```

环境部署按 D 手册进行。辅助脚本不部署靶场、不调用模型、不执行 POC。手册中的 `~/llm-web-lab` 可替换为你自己的仓库路径；已有克隆仓库不需要再运行 `git init`。

## 协作

见 [协作规范](CONTRIBUTING.md) 和 [启动任务](docs/启动任务.md)。每人使用独立分支，以 Pull Request 提交自己的成果并交叉复核。当前 Markdown 文档为协作编辑版；Word 是初始化快照，修改后应统一重新导出。

所有验证仅用于授权的本地教学靶场；证据提交前去除登录 Cookie、令牌与个人信息。第三方源码保留来源、提交号和原许可证；本仓库暂未授予统一开源许可证。
