# C 冻结签字核对清单

> 维护人：C　日期：2026-10-19　分支：`c/review-s017-s022`（已合并 `origin/a/criteria-and-sql01@5b0560a`，含 A 承诺推送的 `382224e`、`abd2014`）
> 用途：对照 `docs/B_冻结签字交接单_2026-10-19.md` 中 C 的确认项，产出逐项核对依据，供本人核对后签字。本清单只记录"输入包/源码/证据"层面事实，不代签、不写运行结果、不填真值。

## 〇、C 确认项（交接单原文）

> **C**：确认 24 个正式输入包、行号映射、源码哈希和版本；确认正式测试使用最终包，不混入归档 v1 包。

## 一、逐项核对结论

| # | 核对项 | 结论 | 依据 |
|---|---|---|---|
| 1 | 24 个正式输入包唯一路径 | ✅ | §二 终检表；每测试样本在 `dataset/packets/` 下唯一对应一个正式包 |
| 2 | 行号映射与源码逐行一致 | ✅ | 24 包 `files[].start/end` 均等于源码实际 `splitlines()` 行数（重点复核 S017/S018 1–57、S021/S022 submit 1–48 / list 1–33 / preview 1–42） |
| 3 | 源码哈希（LF 口径）与 `source.json`/`manifest.case_code_sha256` 一致 | ✅ | 每文件 `files[].sha256` = 源码 LF SHA-256 = `source.json.files[].sha256`；单文件样本 `case_code_sha256`=该文件哈希，多文件样本按 `相对路径<TAB>哈希\n` 聚合一致 |
| 4 | 版本正确（S009–S012 用 v2，其余 v1） | ✅ | S009–S012 正式目录为 `S0xx_v2`，S013–S024 与 S001–S008 为 `S0xx_v1` |
| 5 | 正式测试不混入归档 v1 包 | ✅ | §三 归档隔离 + §四 freeze_plan 只读预检：12 测试样本各唯一对应 1 个正式包，归档包不参与 |

**总体：5/5 通过，C 可签字。** 无阻塞项；仅 §八 两条非阻塞记录性观察。

## 二、24 包哈希终检表

口径：`packet_sha256` = `code_input.txt` 的 UTF-8/LF 内容 SHA-256；`files[].sha256` = 源码 UTF-8/LF SHA-256。下表 24 包 `packet_sha256` 已按 LF 归一化重算，与 `line_map.json.packet_sha256`、`docs/C_输入包总清单.md`、A 分支 git blob 四方一致（C 本轮脚本 `_c_scratch/verify24.py` 重算，0 处不一致）。

| sample | 家族 | 正式包目录 | `packet_sha256` | 行号/哈希/版本 | 结论 |
|---|---|---|---:|---|---|
| S001 | SQL01 | `S001_v1` | `3a84669c84cee3841bf080bb546069a0367b152476cb163a47e533c6661437e1` | 一致 | ✅ |
| S002 | SQL01 | `S002_v1` | `2a55ab105d2153549d248b39b40f22f7fdbbb3471133192ac46060a2ee1546a7` | 一致 | ✅ |
| S003 | SQL02 | `S003_v1` | `965cfab7cf9654ff767f04f15a060994728d07226cf99346e1b64147d70a98ac` | 一致 | ✅ |
| S004 | SQL02 | `S004_v1` | `9c6ca039383b371e799c7eaa34a2183d852c62bda00947e932c2392ef8032235` | 一致 | ✅ |
| S005 | SQL03 | `S005_v1` | `b229827144f951e72a1f1851709487753473a0c92b34a85787db39a81bf48b5e` | 一致 | ✅ |
| S006 | SQL03 | `S006_v1` | `86bbb4103876ae0b56ea28588ba7135eff8076028c87bf079b0455b6bab60bdb` | 一致 | ✅ |
| S007 | SQL04 | `S007_v1` | `0da0b54298c41a089e37c3e1857b02c1cd2124a121ae41f1eaad4ceb0e72861f` | 一致 | ✅ |
| S008 | SQL04 | `S008_v1` | `0b3a718318ce598616ff47aab0a25b110d8f9cd303378d2c20d941110db09dac` | 一致 | ✅ |
| S009 | SQL05 | `S009_v2` | `7a9dd6065e6bd074801d293c94520d93b3f71f7ece14d3244daad1f765f8a5c4` | 一致 | ✅ |
| S010 | SQL05 | `S010_v2` | `1e32adc03620cfd699350fb5399083304cc75277420eba51697672374c06f58f` | 一致 | ✅ |
| S011 | SQL06 | `S011_v2` | `5b38ba932707b693d705e8b54b2340a5e4b6e84cc68cf47210f9c3f77f9e5299` | 一致（LF 修复） | ✅ |
| S012 | SQL06 | `S012_v2` | `fde871dc44f3eff9841293555a58c7a9f62323306e9a64f91b4f8d3db2be0945` | 一致（LF 修复） | ✅ |
| S013 | XSS01 | `S013_v1` | `154456e20c0d4adc6febf6945c6d14c2b97722a38746a4c7ae1fa87a24a6cb4f` | 一致 | ✅ |
| S014 | XSS01 | `S014_v1` | `7e68e97273ddb20a30ce51c1f1ad1dc0fcb4bc30c248340e41296030cce59f03` | 一致 | ✅ |
| S015 | XSS02 | `S015_v1` | `098b1cade9931f53f2be7437a16f595f75670deb944308a4e1c72f7b253077dc` | 一致 | ✅ |
| S016 | XSS02 | `S016_v1` | `71dbcaaa311f580897e7b2109160e34db33614ad625d3287563fd278672eef24` | 一致 | ✅ |
| S017 | XSS03 | `S017_v1` | `81f3c30168c5012ee06ce8a4adb6ba0930ac20dfab5e8170cc8862fbe94980f8` | 一致 | ✅ |
| S018 | XSS03 | `S018_v1` | `0daa5625730551f204c738eea7b9c23e3a31c5bbd0efff23e94535e006e6c350` | 一致 | ✅ |
| S019 | XSS04 | `S019_v1` | `4ee21e7ded087864991df5d86192e1291e222e410d040b83b1b37aa90b19d9ab` | 一致 | ✅ |
| S020 | XSS04 | `S020_v1` | `64ec2ee56ba873938292418f4342eb3c3233f181e7ed879c2caac4eaa38d953e` | 一致 | ✅ |
| S021 | XSS05 | `S021_v1` | `e881e86713926107fa7db458b38c0e9fc824f5a8d916e2ebb799833e7e7122a5` | 一致 | ✅ |
| S022 | XSS05 | `S022_v1` | `ccf37ff8d9b045f365659a9c66896b669cbd6e5b424defd56c5e385b86bba5bd` | 一致 | ✅ |
| S023 | XSS06 | `S023_v1` | `e47750fd9ff681dc105db0d409800d915a6dd5adfe41d452113e35680b4c3781` | 一致 | ✅ |
| S024 | XSS06 | `S024_v1` | `c78a31862f547c160a20fee6a84e09172afc8da441deed8ff543ad76783a109c` | 一致 | ✅ |

- 源码哈希重点抽验（近期改动 6 包）：S011/S012 `files[].sha256`=`3028eb9c…`/`08a09dcc…`，S017 `360525bf…`、S018 `91008837…`，S021 submit `92e4535c…`/list `842876bd…`/preview `e94973f1…`，S022 submit `11d89ba6…`/list `8130a0b9…`/preview `8a615eec…`，全部 = LF 源码哈希 = `source.json`（多文件另与 `manifest.case_code_sha256` 聚合一致）。S009/S010 v2 不受 S011/S012 LF 修复影响。

## 三、归档隔离结论

- `dataset/archive/packets/` 下现存 4 个归档目录：`S009_v1_superseded`、`S010_v1_superseded`、`S011_v1_superseded`、`S012_v1_superseded`。
- 这 4 个归档目录**不在** `dataset/packets/` 下；`tools/freeze_plan.py` 的 `_packet_hashes()` 与 `tools/check_freeze.py` 的 `packet_index` 都只 `glob dataset/packets/**/code_input.txt`，**不覆盖 `dataset/archive/`**。
- 结论：S009–S012 的归档 v1 不参与 36 条正式计划的输入包索引，正式测试只会使用 `S009_v2/S010_v2/S011_v2/S012_v2`。CTX 变体在 `experiments/context_ablation/`，同样不在 `dataset/packets/`，不计入测试样本。

## 四、freeze_plan 只读预检摘要（A 最新分支，未 --write）

- `python tools/freeze_plan.py --model-display-name "DeepSeek-V4.1-Flash" --model-settings "深度思考=开；联网搜索=关"`（不带 `--write`）→ `DRY RUN READY: 36 records`。
- `python tools/check_freeze.py --report-only` → `BLOCKED`，阻塞项共 108 条，全部为正式计划尚未写入的字段：`INVALID_PACKET_SHA256`×36、`INVALID_PROMPT_SHA256`×36、`MODEL_NOT_LOCKED`×36。**没有任何**源码哈希、行号映射、归档包、样本集合类阻塞。
- 含义：36 条计划派生时，每个测试样本唯一对应一个正式包的 `packet_sha256`；只读预检通过，`--write` 须待四人签字后由 A 执行。

## 五、C 名下九条计划（S009 / S012 / S023 × V0/V1/V2）

`runs/formal.json` 中 `operator=C` 共 9 条，均为 `phase=formal`、`status=planned`、`reviewer=B`（符合交换复核规则）。派生 `packet_sha256`（同一样本三版 Prompt 使用同一输入包）：

| run_id | sample_id | 版本目录 | packet_sha256 |
|---|---|---|---|
| F_S009_V0/V1/V2_R1 | S009 | `S009_v2` | `7a9dd6065e6bd074801d293c94520d93b3f71f7ece14d3244daad1f765f8a5c4` |
| F_S012_V0/V1/V2_R1 | S012 | `S012_v2` | `fde871dc44f3eff9841293555a58c7a9f62323306e9a64f91b4f8d3db2be0945` |
| F_S023_V0/V1/V2_R1 | S023 | `S023_v1` | `e47750fd9ff681dc105db0d409800d915a6dd5adfe41d452113e35680b4c3781` |

## 六、S017–S024 动态参考证据复核（Task 2 第一档）

对 A 分支 `evidence/truth/S017–S024` 逐例核对（`browser_reference.json` + `business_http.json`；`current_source_review.json` 仅存在于 6 个改动样本 S011/S012/S017/S018/S021/S022，与源码变更范围一致）：

| 样本 | 家族 | 正常业务请求 | 受控 payload | 观察与蓝图一致 | 漏洞例 marker=yes / 修复例=no | Fatal/DB 异常回显 |
|---|---|---|---|---|---|---|
| S017/S018 | XSS03 | ✅ GET 空列表→POST→303→GET 同页读 | ✅ `<script>…labXss='yes'</script>` | ✅ 写入→303→同页读取 | ✅ S017 yes / S018 no | 无 |
| S019/S020 | XSS04 | ✅ GET 表单→POST 同响应预览 | ✅ 同上 payload | ✅ 模板 sink 预览区 | ✅ S019 yes / S020 no | 无 |
| S021/S022 | XSS05 | ✅ submit→list→preview 三页 | ✅ 同上 payload | ✅ 跨页第二读取路径（preview 渲染正文） | ✅ S021 yes / S022 no | 无 |
| S023/S024 | XSS06 | ✅ GET 表单 + 普通 URL 展示 | ✅ `javascript:void(...labXss='yes')` | ✅ href 实际点击才导航 | ✅ S023 yes / S024 no | 无 |

- 正常业务请求与受控 payload 成对存在：`business_http.json` 记录良性业务流，`browser_reference.json` 记录受控 XSS payload 的 DOM 观察。
- 全部 `php_fatal_error_visible=false`；`runtime_check.json` 报 `37/37` 通过（`runtime_check.passed=37`）。
- marker 仅设置本地 DOM `document.documentElement.dataset.labXss`，无 Cookie 访问、无外部请求、无真实 POC 外传行为（与 A 技术复核记录一致）。

## 七、6 样本待 D 复跑（容器仍跑旧源码，非阻塞真值）

关键证据：D 环境检查 `environment/runtime_check.json` 中容器源码哈希 ≠ 当前正式包 `line_map` 源码哈希，证明容器运行的是 **pre-try/catch 旧源码**（`d_source=a296e4b`），而 A 已把 6 样本源码更新为统一 `try/catch(Throwable)` 口径：

| 样本 | 容器旧哈希（runtime_check，前 12 位） | 当前哈希（line_map，前 12 位） | 差异（A `current_source_review.json` 裁定） |
|---|---|---|---|
| S011 | index `0ec694a2…` | `3028eb9c…` | 查询块 `result===false` → `try/catch(Throwable)`；SQL 构造/可达性/输出不变 |
| S012 | index `624ec128…` | `08a09dcc…` | 同上（fixed 白名单不变） |
| S017 | index `85ac1095…` | `360525bf…` | 仅 insert/list 套 try/catch + 服务端日志；sink `index.php:53` 不变 |
| S018 | index `10f31cfa…` | `91008837…` | 同上；sink `index.php:53`（htmlspecialchars）不变 |
| S021 | submit `36d47353…` / list `77f96bda…` / preview `cdc6464c…` | `92e4535c…` / `842876bd…` / `e94973f1…` | 仅 DB 流程套 try/catch；sink `preview.php:39` 不变 |
| S022 | submit `36d47353…` / list `77f96bda…` / preview `794ab18c…` | `11d89ba6…` / `8130a0b9…` / `8a615eec…` | 同上；sink `preview.php:39`（htmlspecialchars）不变 |

- A 已在 `current_source_review.json` 逐例裁定 `security_flow_unchanged=true`、`new_runtime_execution_claimed=false`，且声明对真值不阻塞；C 复核确认 `unchanged_security_sink` 行号与输入包行号一致。
- **待 D 动作**：按当前 `case_code_sha256` 部署新源码，复跑 6 样本的普通业务、受控 XSS/SQLi 与数据库异常，确认异常不回显、marker 结果不变。

## 八、Chrome→Edge 回退意见与证据来源记录（Task 2 第二档）

**事实（已核实，`abd2014` 已推送）**：
- `abd2014` 提交信息为 `evidence(d): record local runtime and browser references`（D 的证据，作者 D 身份，时间 2026-10-19 15:52 +0800），并非"A 代跑"提交。A 的技术复核记录亦表述为"S017–S024 浏览器记录来源为 D 提交，实际浏览器为 Edge 155"。
- 全部 S013–S024 `browser_reference.json` 的 `browser_version = "Edg/155.0.4283.45"`（Edge 155），本机 Chrome 不存在。

**C 书面意见（Chrome→Edge 回退）**：
- Edge 155 与 Chrome 同为 Chromium 内核，本实验 XSS 判定基于 DOM marker `document.documentElement.dataset.labXss`（本地 `data-lab-xss` 属性），不依赖任何浏览器专有 API、扩展或非标准行为。
- 预期该回退不影响证据解释；实际记录已推送并完成复核，S017–S024 的 marker 观察（漏洞例 yes、修复例 no）与输入包行号、真值蓝图一致，故 C 认可其证据效力。
- 需以实际记录为准已满足（记录在案）。

**非阻塞记录性观察**：
1. S023/S024 的 `browser_reference.json.note` 写"A Chrome mouse press/release clicked…"，与 `browser_version=Edg/155` 措辞不一致（模板残留"Chrome"，实际为 Edge）。仅记录性，不影响 marker 判定。
2. `current_source_review.json` 的 `runtime_evidence_source_commit`（S017–S022 为 `a90708be`，即 D 证据刷新提交）与 `browser_reference.json` 的 `d_source_commit`（`a296e4b`，源码提交）字段语义不同但源码内容一致（`a90708be` 为证据-only 提交，不改源码），无实质冲突。

## 九、C 签字（已提交）

> 签字：C（Chang_jia_jia，1715172213@qq.com）　　日期时间：2026-10-19 16:37（UTC+8）
> 确认范围：本人已核对 24 个正式输入包的唯一路径、行号映射、源码 LF 哈希与版本（S009–S012 用 v2，其余 v1），并确认正式测试使用最终包、不混入归档 v1 包。
> 签字位置：`docs/B_冻结签字交接单_2026-10-19.md` 的 C 节（与 A `97ab7bd` 同一份冻结单）。

---

## 附：可发送群消息（三段）

**① 给 A**

> C 的冻结终检已完成并合入 `c/review-s017-s022`（已合并 `origin/a/criteria-and-sql01@5b0560a`，含 `382224e`、`abd2014`）。24 包哈希/行号/源码哈希/版本四方一致，`freeze_plan.py` 只读预检 `DRY RUN READY: 36 records`，归档 v1 不参与正式计划，C 可签字。Q6/Q7 复核报告与签字核对清单已就绪。S017–S024 的 Edge 155 浏览器证据（`abd2014`，实为 D 证据）已复核、marker 与蓝图一致，C 认可其效力；遗留 6 样本（S011/S012/S017/S018/S021/S022）容器仍跑 `a296e4b` 旧源码，请推动 D 按当前 `case_code_sha256` 复跑。

**② 给 B**

> C 复核确认：S017/S018 最终输入包（`packet_sha256 = 81f3c301… / 0daa5625…`）与 B 三轮开发（V0/V1/V2）metadata 记录的 `packet_sha256` 一致，B 三轮未混入归档 v1，输入包版本无误。S017/S018/S021/S022 四包静态复核通过（差异仅 `index.php:53` / `preview.php:39` 的 echo vs `htmlspecialchars`）。CTX 变体（S007/S020 entry-only）已备于 `experiments/context_ablation/`，按裁定在主实验 36 条归档后独立执行。

**③ 给 D**

> C 对 Chrome→Edge 回退的书面意见：Edge 155 与 Chrome 同为 Chromium 内核，XSS 判定基于 DOM marker `data-lab-xss`，预期不影响证据解释，已按实际记录复核认可。请 D 按当前 `case_code_sha256` 复跑 S011/S012/S017/S018/S021/S022 六样本（普通业务 + 受控 payload + 数据库异常），确认异常不回显、marker 结果不变后完成 D 签字。
