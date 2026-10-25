# S001 evidence quarantine notice

日期：2026-10-26（Asia/Shanghai）

## 结论

S001 官方八条证据包暂不接受。该结论不否定八条模型的静态漏洞判断，只表示当前归档材料无法证明截图、raw、normalized、metadata、Prompt 和完整输入属于同一次真实会话。

## 已识别问题

- raw、截图、normalized、metadata 存在跨轮次混用；
- 部分 raw 夹带下一条回答；
- SAFE_BASE 存在不同 JSON 版本；
- LEAK_DEF 与 DIVERT_BASE 存在错绑或复用风险；
- 截图中的 source、location、missing_context 与归档回答不一致；
- 会话 URL 存在，但不能单独证明完整输入和生成设置；
- 旧材料在合并前未完成逐条最终绑定检查。

## 处置

- 八条继续保持 `planned`；
- 不修改 36 条正式记录；
- 不将旧 raw、截图或 normalized 复用为新运行证据；
- 旧材料仅保留为审计历史，待新一轮证据替换；
- C 的不通过结论视为有效发现，不归责于 C。

## 重建门槛

每条必须从同一个新会话生成并绑定：完整 input.txt、raw_output.txt、normalized.json、metadata.json、Prompt/input/raw 三类 SHA-256、该会话设置截图、该会话回答截图和 session URL。SAFE_BASE 的原始格式缺陷必须原样保留。
