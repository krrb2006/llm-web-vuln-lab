# A 代做 C/D 技术复核记录（2026-10-19）

## 结论

本记录是 A 代 C/D 完成的技术检查，不代替 C/D 的人工确认和冻结签字。

- C 输入包复核：通过，24/24。
- D 环境与参考证据复核：通过。
- 正式运行：未开始。
- 真值字段：未由本记录修改；参考证据继续保留 `ground_truth=null`。
- C/D 签字：待本人确认。

## C 部分：输入包、行号映射和源码哈希

按当前 A 工作树逐项检查了 S001—S024：

1. 24 个样本均为 `ready`，正式包文件和 `line_map.json` 均存在。
2. S009—S012 使用 `v2` 包，其余样本使用当前正式 `v1` 包；已归档的 S009—S012 v1 未参与检查。
3. 24 个 `code_input.txt` 的 LF 规范化 SHA-256 与 `line_map.json.packet_sha256` 一致。
4. `line_map.json` 中的文件范围、样本编号和源码 SHA-256 一致；源码哈希按 LF 口径核对。
5. 重点复核 S017、S018、S021、S022，四例的包正文、行号映射和源码哈希均通过。
6. 未发现把 `manifest`、真值卡、样本卡或 `line_map.json` 混入模型输入包的情况。

## D 部分：环境和参考证据

环境参考记录来自以下来源：

- A 源提交：`173b9af0da6701b9b43a2cae53d5ae240b6df9ef`
- C 源提交：`8da63f7b8e169e5037626b0362d005ba7ba5ede0`
- D 源提交：`a296e4b527ebdaf41ca04c2bbc5627b1a89efc06`
- DVWA 提交：`a1978a2fed195acd093010af6395f86a281537ca`
- 靶场地址：`127.0.0.1:4280`

检查结果：

1. PHP 文件运行检查 `37/37`，失败数为 `0`，DVWA 配置哈希通过。
2. S001—S012 的普通 HTTP 参考记录齐全，未发现可见 PHP fatal error。
3. S013—S016 的浏览器 DOM 参考记录齐全；本机 Chrome 不存在，使用 Edge 155 完成，正常/marker 观察与样本配对预期一致。
4. S017—S024 的普通业务 HTTP 和浏览器参考记录齐全；浏览器记录来源为 D 提交，实际浏览器为 Edge 155。
5. S021/S022 的观察符合“提交写入、列表展示标题、独立 preview 读取正文”的第二读取路径；S021 marker 可执行，S022 未执行。
6. 所有 marker 仅设置本地 DOM 的 `document.documentElement.dataset.labXss`，没有 Cookie 访问、外部请求或真实 POC 外传行为。
7. 所有本轮参考记录仍为 `ground_truth=null`；S017—S024 仍标记为 `pending_independent_review`，没有把参考观察冒充模型结果或 POC 触发证据。

## 冻结状态

B 的冻结签字交接单已从 `9da7fb4` cherry-pick 到 A 分支，对应本地提交为 `97ab7bd`。签字单当前仍是待四人签字状态。

`freeze_plan.py` 只读预检可以派生 36 条计划；`check_freeze.py --report-only` 的当前阻塞仅是正式计划尚未写入模型、Prompt 和输入包字段。这些字段必须在四人真实签字后由 A 执行 `freeze_plan.py --write` 写入。

本记录不代签 C/D。C、D 只需复核本记录与对应证据，若无异议，在冻结签字交接单中完成本人确认；如有异议，应提交具体文件、行号或新运行证据。
