# 本目录统计已被 `results/formal_eval_2026-11-01-v3/` 取代

本目录的 `summary.json` / `summary.md` 是 2026-10-19 首次冻结的统计，**仅作历史留档，不要再引用为当前结论**。

## 为什么不再一致

- 本目录统计由提交 `0c994ed`（record complete formal experiment results）生成，之后未再更新。
- 同一批 36 条正式记录 `runs/formal.json` 随后被补齐/更正：
  - `4bf4a35` evidence(b): execute S019 localhost POCs with browser pending
  - `5bd9609` evidence(b): bind S019 V2 browser trigger evidence
  - `259dc1c` audit: accept S001 evidence and correct model provenance
- 用现行 `runs/formal.json` 重算，2026-10-19 冻结值有 12 个字段漂移（分类与定位指标不变）：

| 字段 | 2026-10-19 冻结 | 2026-11-01 重算 |
|---|---:|---:|
| V0 原始 POC 可执行率 | 0.0% | 20.0% |
| V2 原始 POC 可执行率 | 16.7% | 33.3% |
| V2 实际触发条数 | 1 | 2 |
| V0/XSS、V2/XSS 分层的 POC 可执行与触发字段 | 0 | 20.0%–33.3% |

## 现行口径

`results/formal_eval_2026-11-01-v3/summary.json` 与 `summary.md` 由 `tools/evaluate.py` 直接从 `runs/formal.json` 生成，未手工编辑；`tools/audit_submission.py` 的“统计与记录一致”检查项会在两者不一致时报警。

复算命令：

```bash
python tools/evaluate.py --manifest dataset/manifest.json --runs runs/formal.json --root . --out results/<新目录>
```
