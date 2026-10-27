# C 最终仓库一致性修正记录（2026-10-26）

基线：`a/criteria-and-sql01@c5248ea`

## 结论

正式实验 36/36 和加分实验 26/26 的状态、统计及原始证据保持不变。S001 八条继续记录为 `status=reviewed`、`operator=D`、`reviewer=A_self_review`；这是 A 对 D 运行证据完成的项目内自审，不是 C 独立复核签字。团队已决定 C 签字属于可信度增强项，不是提交阻塞项。

## 本次修正

1. 八份 S001 metadata 不再把平台公告映射写成逐会话直接证明：
   - `model_display_name=null`；
   - `model_version_proven=false`；
   - `model_version_inferred=DeepSeek-V4.1-Flash-1017`；
   - `model_version_inference_scope=official_platform_announcement`；
   - `per_run_model_field_captured=false` 保持不变；
   - `exploratory_only=false` 保持不变，因为团队已将本批记录接入官方加分计划。
2. S001 汇总与 D 的交接说明对齐当前审核身份，删除“必须等待 C 签字”的现行要求；对 D 文件的修订均增加 C 修订说明，不改变 D 的运行记录和署名。
3. 最终 Markdown 报告和 Word 生成源补充实际业务判据：除 exit code 0 外，八条记录还依据普通/测试请求中的 Alice、Bob、Carol 记录或真假条件响应差异；没有把 HTTP 200 或退出码单独当作漏洞触发。
4. 最终报告明确 `operator=D`、`reviewer=A_self_review`，不声称 C 独立复核通过。

## 保持不变

- 不修改任何模型 raw、normalized、input、截图、POC、stdout/stderr 或执行时间；
- 不修改 `runs/formal.json`、36 条正式实验、bonus 的 reviewed 状态和 26/26 统计；
- 不重跑模型或 POC；
- ADV 四条仍由 D 独立复核，POC 仍明确为 `not_run`；
- `DeepSeek-V4.1-Flash-1017` 仅作为官方平台公告推定版本，不作为单次会话直接实测字段。

## 发布提醒

最终集成分支为 `a/criteria-and-sql01`。仓库默认 `main` 尚未包含该分支的完整结果，面向 main 的 PR #1 应更新为最终交付说明，并在合并或明确提交分支后再宣称仓库发布完成。

C（squeezeash-hue）　2026-10-26（UTC+8）
