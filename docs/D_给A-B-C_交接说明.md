# D 给 A、B、C 的交接说明（2026-10-11）

2026-10-11 的原始运行基线为 A `d498903da01d89a695fa49d5392d3776eb901e2f`、C `a04a83218e7999acd03d8a20422cf4b405903479`、D `a296e4b527ebdaf41ca04c2bbc5627b1a89efc06`。2026-10-13，D 已按 C 新提交 `8da63f7b8e169e5037626b0362d005ba7ba5ede0` 重建运行树并重验 S009/S010；结果见 `environment/runtime_check.json` 和对应 HTTP 参考记录。所有 `ground_truth` 仍为 `null`，以下内部资料不发送给模型。

## 给 A：独立复核 D 样本与真值

**接收文件**：`dataset/raw/S017`–`S024` 的 PHP、`source.json`、`sample_card.md`、`reference_check.md`；`environment/runtime_check.json`；`evidence/truth/S017`–`S024` 中每例的 `business_http.json` 与 `browser_reference.json`；`docs/D_第二轮样本交接.md`。

1. 按固定源码逐例核对普通业务、输入到输出的数据流、受控浏览器观察和配对差异。存储型案例要核对写入与另一次读取；S023/S024 要核对实际点击前后的 DOM，不能只看 `href` 文本。
2. **重点确认 XSS05 S021/S022**：C 手册写“第二条读取路径”，现实现为 `submit.php` 写入、`list.php` 显示标题、`preview.php` 显示正文。请与 C 商定这是否满足蓝图；若需要改源码，先修订固定版本、哈希、输入包与受影响证据，不沿用旧结论。
3. 为 D 构造的八例独立签署真值复核记录；存在争议先记录原因和处理结果，再由负责同学更新 `dataset/manifest.json` 的 `ground_truth`、`truth_reviewer`、`truth_evidence` 与状态。构造目标、D 的参考观察或 HTTP 200 均不能直接代替复核。
4. 第一轮 A 自建 S001–S008 的运行参考见 `docs/D_第一轮参考验证交接.md` 与相应 `evidence/truth` 目录；按总手册组织交叉复核。正式运行阶段 A 的 S007/S020/S021 九条记录由 D 复核，届时需提供原始输出、适配记录与运行证据。

## 给 C：复核第一轮并制作中性输入包

**接收文件**：`evidence/truth/S009`–`S016` 的 HTTP/浏览器记录，`docs/D_第一轮参考验证交接.md`；D 的 `dataset/raw/S017`–`S024`、`source.json`、`context.txt` 与 `environment/runtime_check.json`；第二轮每例业务和浏览器 JSON。

1. 独立复核 S009–S016 的源码、正常路径与受控观察。S009/S010 已按 C 的新提交 `8da63f7b8e169e5037626b0362d005ba7ba5ede0` 由 D 重验。S009 的 `ids=1 OR 1=1` 实测仅返回 ID 1，`ids=1) OR 1=1 #` 返回三行；尾随空格注释现在 HTTP 200、空结果且不显示 PHP Fatal error。S010 回归观察也已更新。两份证据的 `ground_truth` 仍为 `null`。请复核 S009 v2 `code_input.txt` 哈希：D 从仓库计算为 `7a9dd6065e6bd074801d293c94520d93b3f71f7ece14d3244daad1f765f8a5c4`，与 B 通知的 `7a95dd606…` 不一致；S010 v2 为 `1e32adc03620cfd699350fb5399083304cc75277420eba51697672374c06f58f`。S009 对齐前不要冻结该包。
2. 与 A 核对 S021/S022 是否符合 XSS05 蓝图。未定稿前不静默修改 D 已固定的 PHP 文件。
3. 为 S017–S024 生成并验收中性 `dataset/specs`、`dataset/packets` 和原始行号映射。S019/S020 同时包含控制器与模板；S021/S022 包含写入、列表、预览三个页面；S017/S018、S021/S022 准确说明共用 mysqli 连接和教学表，排除密码。逐包排查内部构造目标、配对说明、样本卡、参考验证和真值泄漏，再交 B 试读。
4. 正式阶段 C 复核 D 的 S010/S011/S022 九条记录；D 的记录须在样本、输入包、环境、真值和 Prompt 冻结后才生成。

## 给 B：Prompt、模型输出与冻结

**接收文件**：C 验收后的 `code_input.txt` 与中性运行上下文、A 的判定规则、`environment/README.md` 的本地运行前提。`source.json`、行号映射、内部样本卡、真值和参考证据供组内追溯，不进入模型输入。

1. 仓库已有六份候选场景 Prompt。请按 B 手册确认 V0/V1/V2 的差异、输出字段契约和定稿文本；保留各版哈希、模型名称及版本、会话设置和原始输出。协调 A/C/D 确认冻结清单，明确同一输入包和环境用于正式比较。
2. 在冻结前检查中性输入是否足以看懂跨文件数据流，尤其 S019/S020 的模板与 S021/S022 的三页面流程；发现缺上下文交给 C 修订并重新计算输入包哈希。
3. 正式阶段 B 执行 S008/S019/S024 各 V0/V1/V2 九条记录，保留模型原始输出、人工适配和现场证据，并交 A 复核。D 的本机参考证据不计入模型成绩。

## D 接下来的依赖

D 配合 A/C 复核争议，按冻结提交重做任何受影响的语法、哈希、正常业务与浏览器检查。冻结完成后，D 执行 S010/S011/S022 的九条正式记录并复核 A 的九条，交 C 复核本人记录。本机 Burp 已安装。10 月 13 日经 Burp Proxy 完成首轮 S009/S010 SQL 对照以及 S021/S022 的普通/marker 提交、列表与预览请求；XSS 的代理正文、DOM 和两张浏览器截图保存在 demo 观察记录中，首轮演示行已清理。D 已在 Burp Repeater 手工重放 S021 `id=15` 和 S022 `id=16`，并完成 S009/S010 四条只读 SQL 对照；全部返回 HTTP 200，正文观察符合预期。SQLi 的 Repeater 观察摘要和截图见 `demo/burp_sqli_repeater_observation.json` 与对应 JPG；最新 S009 受控条件的 raw 请求/响应已保存于 `demo/S009_request.raw.txt`、`demo/S009_response.raw.txt`，其余三条 SQLi Repeater raw 消息与第二台电脑复现仍未完成。S021/S022 重试行暂留供复核。

## MySQLi 异常处理口径（D 选择，待 A 确认）

D 选择保留 PHP mysqli 严格异常模式，并建议在所有样本的完整查询流程（query/prepare/bind/execute/result）外统一使用 `try/catch (Throwable)`。catch 只调用 `error_log()` 并返回普通错误提示或空结果，不将异常文本写入页面；不在公共连接文件设置 `MYSQLI_REPORT_OFF`。S009/S010 已有样本内捕获。请 A 对 S001–S008 采用同一口径；A 确认后由 C 对齐 S011/S012。来源提交更新后，D 重建运行树并复核语法、哈希和错误输入的页面回显。
