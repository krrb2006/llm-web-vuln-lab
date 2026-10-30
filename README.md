# LLM 辅助 Web 漏洞挖掘与验证

网络安全课程四人小组大实验：使用大语言模型辅助审计受控 PHP Web 样本，重点覆盖 SQL 注入（SQLi）和跨站脚本（XSS），并通过源码真值、结构化模型记录、人工复核和本地教学靶场验证形成完整证据链。

**当前状态：正式实验 36/36、加分实验 26/26 均已归档并完成项目内复核；自动化测试 22/22 通过。SQLi/XSS 主实验在本组样本上的三版 Prompt 均为 12/12 分类正确、12/12 定位正确，不将该结果外推为真实世界准确率。**

首先阅读：[代码说明_测试指南.docx](代码说明_测试指南.docx)。该文档完整说明环境准备、代码作者、测试命令、Docker/DVWA 启动、样本复核、作者查询和常见错误处理。

最终交付报告：[Word 版](docs/网络安全大作业实验报告.docx) · [PDF 版](docs/网络安全大作业实验报告.pdf) · [Markdown 源稿](docs/最终实验报告_2026-10-26.md) · [教师测试指南 Markdown 版](docs/代码说明_教师测试指南.md) · [代码作者索引](AUTHORS.md)

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

代码作者与分工见[教师测试指南](docs/代码说明_教师测试指南.md)和[代码作者索引](AUTHORS.md)：A 刘珂如、B 张思佳、C 常佳佳、D 李楠。遇到错误时，可执行 `python tools/show_author.py <报错文件路径>` 直接反查作者。

## 代码作者与错误查询

|路径|作者|主要职责|
|---|---|---|
|`tools/`、`tests/`|A 刘珂如|冻结检查、提交审计、指标评估和项目测试|
|`prompts/`|B 张思佳|SQLi/XSS Prompt、版本迭代和模型输入|
|`dataset/`、`submission_inputs/`|C 常佳佳|样本源码、预处理、输入包和数据追溯|
|`environment/`、`pocs/`、`evidence/`、`demo/`|D 李楠|Docker/DVWA、POC、Burp 和运行证据|
|`docs/A_*`、`results/A_*`|A 刘珂如|判定、真值、复核、统计和最终整合|
|`docs/B_*`、`results/B_*`|B 张思佳|Prompt 实验和迭代分析|
|`docs/C_*`、`results/C_*`|C 常佳佳|样本审核、输入包和独立复核|
|`docs/D_*`、`results/D_*`|D 李楠|环境、POC、Burp 和运行复核|
|`runs/`、`experiments/`、`templates/`|全组协作|模型运行、加分实验和共同模板|

老师遇到运行错误时，请在仓库根目录执行：

```powershell
python tools/show_author.py <报错文件路径>
```

例如：

```powershell
python tools/show_author.py environment/check_runtime.py
```

该脚本会输出作者、职责和对应操作手册；完整映射见 `AUTHORS.md`。

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
|tools/|冻结、审计、评估、输入准备和证据索引工具|
|tests/|冻结检查、审计、统计和本地分析自动化测试|
|experiments/|Prompt 注入、Burp 联动、上下文消融、二次注入与逻辑漏洞加分实验|
|demo/|Burp 联动请求、响应、截图和演示材料|

正式数据和证据已经冻结；正式统计使用 `runs/formal.json` 和 `dataset/manifest.json`，加分实验单独保存在 `experiments/`、`runs/` 和 `evidence/` 中，不回写主实验指标。

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

正常检查结果应为：`Ran 22 tests ... OK`、冻结检查 `READY`、提交审计的正式实验和加分实验状态 `READY`。如果出现 `ModuleNotFoundError: tools...`，请确认当前目录是包含 `tools/`、`tests/` 和 `dataset/` 的仓库根目录。

## 本地教学靶场测试

动态验证仅用于授权的本地教学靶场，服务绑定 `127.0.0.1:4280`，不用于公网扫描或攻击。首次使用时按 `environment/README.md` 准备 DVWA：

```powershell
git clone https://github.com/digininja/DVWA.git third_party/DVWA
$aRef = 'd498903da01d89a695fa49d5392d3776eb901e2f'
$cRef = '8da63f7b8e169e5037626b0362d005ba7ba5ede0'
$dRef = 'a296e4b527ebdaf41ca04c2bbc5627b1a89efc06'
python environment/build_lab_cases.py --a-ref $aRef --c-ref $cRef --d-ref $dRef
python environment/init_lab_db.py
docker compose --env-file local/lab.env -f third_party/DVWA/compose.yml -f environment/compose.lab.yml up -d
```

浏览器访问 `http://127.0.0.1:4280/`，再执行：

```powershell
python environment/check_runtime.py --a-ref $aRef --c-ref $cRef --d-ref $dRef
python environment/check_sql_http.py --sample S009 --sample S010
python environment/check_xss_browser.py
python environment/check_d_business.py
```

结束后执行：

```powershell
docker compose --env-file local/lab.env -f third_party/DVWA/compose.yml -f environment/compose.lab.yml down
```

不要使用 `docker compose down -v`，以免删除 DVWA 数据卷；不要提交 `local/lab.env`、登录 Cookie、令牌或未脱敏截图。

## 样本和证据复核

1. 在 `dataset/manifest.json` 找到样本编号、漏洞类型和真值记录。
2. 在 `dataset/raw/<sample_id>/` 阅读原始 PHP、样本卡和真值复核说明。
3. 在 `dataset/packets/` 查看固定输入和 `line_map.json`。
4. 在 `runs/F_<sample>_<version>_R1/` 查看模型原文、规范化 JSON、输入哈希和运行元数据。
5. 在 `pocs/`、`evidence/` 和 `demo/` 查看 POC、请求响应、截图和复核记录。
6. 对照 `results/`，区分模型预测、代码定位、原始 POC 可执行和实际漏洞触发。

HTTP 200、脚本退出码 0 或模型回答本身都不能单独证明漏洞成立；必须结合源码数据流、普通/受控请求和预先定义的观察判据。

## 最终交付与实验边界

- 正式统计使用冻结后的 36 条记录，加分实验不回写主实验指标；
- 原始 POC、环境适配 POC 和逻辑修改版 POC 分开记录；
- 部分加分记录采用项目内自复核，报告中已明确标注，不冒充外部独立复核；
- 实验结果只描述本组受控教学样本，不代表模型的通用漏洞发现能力；
- 提交给老师的源代码压缩包应包含源码、实验数据、报告和根目录 `代码说明_测试指南.docx`，但不包含 `.git/`、`local/lab.env`、个人 Cookie、令牌或未脱敏材料。

## 协作

见 [协作规范](CONTRIBUTING.md) 和 [启动任务](docs/启动任务.md)。每人使用独立分支，以 Pull Request 提交自己的成果并交叉复核；最终交付内容已合并到 `main`。

所有验证仅用于授权的本地教学靶场；证据提交前去除登录 Cookie、令牌与个人信息。第三方源码保留来源、提交号和原许可证；本仓库暂未授予统一开源许可证。
