# D 对 CTX 上下文消融的复核发现（2026-10-19）

复核人：D（不是 CTX 的 primary reviewer；本记录是独立技术复核，供 A/C 裁定）
对象：`experiments/context_ablation/runs/CTX_S007_ENTRY/FULL`、`CTX_S020_ENTRY/FULL`，基线 `e69e93f`
状态：4 条均为 `executed`，reviewer 为 A；D 未改动任何 CTX 记录或状态。

## 一、事实

四条 CTX 记录的 `metadata.json` 中 `prompt_sha256` 均为：

```text
3666ebeb28980e192172852639ab1759c94b6cbb2e5cdfe0c6f185a946841178
```

该哈希对应 `prompts/XSS_V2.txt`，不是 `prompts/SQLi_V2.txt`（`8f2fcafb576e990d…`）。

而 S007 在 `dataset/manifest.json` 中是 **SQLi** 样本（family SQL04，`case_code_sha256=f7be23ad…`），输入包为 `S007_v1`（`index.php` + `repository.php`）。S020 是 XSS 样本，用 XSS_V2 是正确的。

## 二、影响

1. **S007 的 entry-only / full-context 对比不是同一漏洞类型的对照**：两轮都用 XSS_V2，模型被要求审计 XSS；full-context 输出 `vulnerability_type=SQL注入`、`format_valid=false`，本质是“被问 XSS、却回答了 SQLi”的类型漂移，不能直接归因于“多了 repository.php 上下文”。
2. A 的 CTX 小结把 S007 full-context 的 SQLi 发现描述为上下文带来的收益；如果保留这个结论，报告需要明确“这是在 XSS Prompt 下观察到的跨类型行为”，不能写成 SQLi 上下文消融。
3. S020 的 entry-only `uncertain` → full-context `safe` 是 XSS_V2 对 XSS 样本，类型匹配，结论可用。

## 三、建议（二选一，由 A/C 裁定）

### 方案 A：重跑 S007 两轮（推荐，若时间允许）

- 用 `prompts/SQLi_V2.txt`（`8f2fcafb…`）重跑 `CTX_S007_ENTRY` 与 `CTX_S007_FULL`；
- fragments 与 runtime context 保持与现有 CTX 相同，只改 Prompt 类型；
- 旧的两条保留为“XSS Prompt 跨类型观察”或归档，不覆盖；
- 新记录仍为 `executed_pending_review`，由 A 复核后改 `reviewed`。

### 方案 B：不重跑，改结论口径

- 把 CTX 的题目改为“同一 XSS_V2 Prompt 在 SQLi/XSS 样本上的跨类型表现”，不再声称“S007 的上下文消融”；
- 在报告/PPT 中明确 S007 的 full-context 输出是类型漂移、格式失败，不作为“上下文提升检出”的证据；
- 保留 4 条 `executed`，由 A 在复核记录中注明该设计限制。

## 四、其他小问题

- CTX 四条 `metadata.json` 的 `packet_sha256` 为空；若输入可追溯只靠 `input.txt`，建议补 `input_sha256` 或在记录中说明。
- S007 FULL 的 POC 代码块未执行，`poc_generated=true` 与 `verification` 的边界需在 A 的复核记录中写清，不要被统计成“POC 触发”。
- 主实验 36 条未受影响；本发现只影响加分实验的解释口径。

## 五、签字

D（linan / linan-prog，2986713478@qq.com）　2026-10-19 23:35（UTC+8）

结论：CTX 4 条已真实归档，但 S007 的 Prompt 类型与样本类型不一致；建议重跑或改写结论口径后再由 A 标 `reviewed`。
