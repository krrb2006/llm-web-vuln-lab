# C 对 D 名下九条正式记录的独立复核（2026-10-20）

> 复核人：C（Chang_jia_jia，1715172213@qq.com）　日期：2026-10-20（UTC+8）　分支：`c/review-s017-s022`
> 对象：D 名下 S010 / S011 / S022 × V0/V1/V2 九条正式记录（`run_id` = `F_S010_*_R1`、`F_S011_*_R1`、`F_S022_*_R1`，`operator=D`、`reviewer=C`）
> 证据来源：`origin/d/formal-nine`（D 的正式运行分支）上的 `runs/`、`evidence/`、`pocs/`；本记录只依据仓库内真实证据下结论，不虚构签字、不把未运行记录判为通过、不把 HTTP 200 或脚本退出码当作漏洞触发证据。

## 一、结论

**九条全部通过 C 的独立复核，结论为「复核通过」。**

| sample | 家族 | 构造目标 → 真值 | 模型预测（V0/V1/V2） | 与真值一致 | POC/执行证据 | 复核结论 |
|---|---|---|---|---|---|---|
| S010 | SQL05（修复版） | fixed → `false` | safe / safe / safe | ✅ | 无 POC（safe 样本，正确不产攻击性 POC） | 通过 |
| S011 | SQL06（漏洞版） | vulnerable → `true` | vulnerable / vulnerable / vulnerable | ✅ | V0 无 POC；V1/V2 POC 已触发（verification=triggered） | 通过 |
| S022 | XSS05（修复版） | fixed → `false` | safe / safe / safe | ✅ | 无 POC（safe 样本） | 通过 |

三条样本的九个版本预测全部与 `ground_truth` 一致：S010（修复版 IN 列表绑定）判 safe、S011（ORDER BY 直接拼接）判 vulnerable、S022（预览 htmlspecialchars 转义）判 safe。模型未出现漏报/误报。

## 二、我独立核对过的证据（逐项）

### 2.1 哈希一致性（全部程序化重算，非采信 D 的自述）

| 核对项 | 方法 | 结果 |
|---|---|---|
| `input_sha256` | `input.txt` 的 LF 规范化 SHA-256 | 9/9 与 metadata 一致 |
| `raw_output_sha256` | `raw_output.txt` 的 LF 规范化 SHA-256 | 9/9 与 metadata 一致 |
| `prompt_sha256` | 与冻结六份 Prompt 哈希比对 | 9/9 命中：SQLi_V0 `94e49bd8…`、SQLi_V1 `76727ec1…`、SQLi_V2 `8f2fcafb…`；XSS_V0 `824ea2c5…`、XSS_V1 `44476daa…`、XSS_V2 `3666ebeb…` |
| `packet_sha256` | 与冻结输入包清单比对 | 9/9 命中：S010 `1e32adc0…`、S011 `5b38ba93…`、S022 `ccf37ff8…` |
| 模型与批次 | metadata 字段 | 9/9 = `DeepSeek-V4.1-Flash`，`model_snapshot=V4.1-Flash-1017`，`深度思考=开；联网搜索=关` |

### 2.2 模型原文与规范化结果

- `format_valid=true` ×9；`poc_format_valid=true` 仅 S011 V1/V2（对应其唯一产出的 POC），其余 7 条 `poc_format_valid=false`（无 POC，正确）。
- S010 三版本 `parsed_json.prediction=safe`，引用行号落在 `ids` 过滤（F01:0016）、占位符构造（F01:0026-0027）、`bind_param`（F01:0030-0031），guard 判「有效」——与修复版源码一致。
- S011 三版本 `parsed_json.prediction=vulnerable`，引用 `sort` 入口（F01:0008）、`ORDER BY $sort` 拼接（F01:0013）、`$db->query()` 执行（F01:0015），guard 判「无效」——与漏洞版源码一致。
- S022 三版本 `parsed_json.prediction=safe`，引用 submit/list/preview 三个文件，最终 sink 判 `htmlspecialchars` 转义（F02:0029、F03:0038-0039）——与修复版源码一致。

### 2.3 POC 与执行证据（S011 V1 / V2）

| 项 | V1 | V2 |
|---|---|---|
| 原文 POC 语言 | python3 | python3 |
| 成功判定 | 排序结果变化，非 HTTP 200 | 排序结果变化，非 HTTP 200 |
| 原脚本运行 | `original.py` 直接运行 exit 1（根路径取不到页面） | `original.py` 未改，用 `ENTRY_PATH=/lab_cases/S011/index.php` 运行 exit 0 |
| 环境适配 | `adapted.py` 仅改 `BASE_URL` 为 `/lab_cases/S011/index.php`，diff 已核对无其它改动 | 无需改动 |
| 普通对照 | `[(1,Alice),(2,Bob),(3,Carol)]` | 同左 |
| 测试输入 | `(id=2) DESC, id ASC` → `[(2,Bob),(1,Alice),(3,Carol)]` | `CASE WHEN … ELSE -id` → `[(3,Carol),(2,Bob),(1,Alice)]` |
| 结果 | 顺序改变，`verification=triggered` | 顺序改变，`verification=triggered` |

两条 POC 均只访问 `127.0.0.1:4280`，无外部主机、无写文件、无删除、无 Cookie 外发，测试输入不修改数据，成功依据是可预测的行序变化而非响应码——符合 POC 安全与判定口径。

### 2.4 截图与归档完整性

- 九条记录各含 3 张截图（`screenshot_answer_1.png`、`screenshot_answer_2.png`、`screenshot_settings.png`），共 27 张，均在位。
- POC 脚本在 `pocs/F_S011_V1_R1/{original.py,adapted.py}`、`pocs/F_S011_V2_R1/original.py`，`adapted.diff` 仅一处 `BASE_URL` 变化（首行 BOM 为无害产物）。

## 三、发现的非阻塞问题（记录在案，不改变结论）

1. **S010 V1/V2 的 `verification.md` 存在复制粘贴笔误**：`正常业务请求与结果` 一栏写成 `GET sort=id / sort=name / sort=name DESC`，并引用 `evidence/truth/S011/http_reference.json`；S010 实际参数为 `ids`（V0 栏写法正确），参考证据应为 S010 自身。该笔误只在 D 的执行记录模板里，模型原文与 `normalized.json` 对 S010 的判定（safe、`ids` 过滤）不受影响，真值亦不变。**建议 D 后续修正文案，不阻塞复核。**
2. **九条 `verification.md` 的「复核人签名和日期」为空**：该栏由复核人 C 填写。C 在本记录末尾签署，作为对九条的复核签字；`origin/d/formal-nine` 上 D 的文件由 D 在集成分支时回填本签字或引用本记录。

## 四、签字

> C（Chang_jia_jia，1715172213@qq.com）　2026-10-20（UTC+8）
> 签字范围：对 D 名下 S010 / S011 / S022 × V0/V1/V2 九条正式记录的独立复核。经程序化重算哈希、逐条比对预测与真值、核对 POC 与执行证据，九条均与 `ground_truth` 一致、证据可追溯、POC 仅作用于本地靶场且非破坏，故**九条全部复核通过**。
> 明确不签署：本记录不代 D 修改 `runs/formal.json` 中 D 名下九条的 `status`（该动作应在 D 记录合入集成分支后，由 C 复核签字后按流程更新为 `reviewed`）；不代签 A/B/D 任何一项。
