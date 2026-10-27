# A 对 S001 重跑证据的接入核验（2026-10-25）

B 的 S001 重跑材料已从 `b/final-audit-2026-10-20` 合入 A，合并提交为 `aa51e8d`。本记录只报告 A 接入后的文件事实，不改变计划状态，也不替代 C 的独立复核。

## 当前已接入

- 8 个 S001 `raw_output_user.txt` 文件。
- 8 个回答截图及一份重复截图文件。
- 8 个 `input.txt`、`normalized.json` 和 `metadata.json` 的更新。
- B 的交接报告、运行回执和 POC 未执行/端点不可用记录。

## A 侧核验发现

- 8 条中只有 `INJ_SQLI_IGNORE_BASE` 的 metadata 当前包含 session URL 和 `raw_output_sha256`。
- 其余 7 条 metadata 仍缺 session URL 和 `raw_output_sha256`，不能据此声称 8 条独立会话已经逐条绑定。
- 8 张回答截图已进入仓库，但当前 metadata 没有为每条记录提供独立的回答截图路径映射。
- 设置证据仍引用共享设置截图，不能单独证明每条会话的模型名称和逐条会话绑定。
- `experiments/bonus_runs.plan.json` 中 S001 8 条仍全部为 `planned`。

## 裁定

本轮不把 S001 8 条改为 `reviewed`，也不提高加分完成数。B 需要补齐或明确披露剩余 7 条的 session/raw 哈希/截图归属；C 收到完整材料后再独立复核。POC 仍不执行。

## 2026-10-25 修订

B 后续提交 `edf762e` 新增 `results/B_S001_rerun_binding_manifest.json`。A 已将其合入 `7203eed`，并逐条核验：8 个 session URL、8 个回答截图、8 个 input SHA-256 和 8 个 raw SHA-256 均能对应当前工作树文件；8 条均声明 POC 未执行。上一节关于“只有一条绑定”的结论仅适用于 manifest 合入前的 A 工作树，现由本节修订。

当前仍保留的限制是共享设置截图、模型名称跳过，以及尚未完成 C 对新绑定清单的独立复核。因此 S001 八条在 C 新复核完成前仍保持 `planned`。
