# S013 核验补充：XSS_V0 哈希

本补充不改写已保留的 [C_S013_independent_audit_2026-10-21.md](C_S013_independent_audit_2026-10-21.md)，也不修改 A 的任何模型原文。

在最新 `origin/a/criteria-and-sql01@93e91454371c3b5d54aed50ad8af5586b5074a71` 隔离分支重新计算后，`prompts/XSS_V0.txt` 的 UTF-8/LF SHA-256 为：

`824ea2c5fba391e0827a554c0683a4738efa38859c2b52f2d1de131634a32bf2`

`environment/prompt_hashes.txt` 中的 `XSS_V0` 现在也是同一完整 64 位值。现有 [C_S013_independent_audit.json](C_S013_independent_audit.json) 的 8 条记录均显示 `prompt_matches_freeze=true`、证据路径存在、计划状态配对正确；四条 BASE 的重复 JSON 键和 DIVERT_BASE 的 POC 格式问题仍按原报告保留，交 B 裁定。原报告中关于旧冻结清单长度的文字属于历史核验时点，故在此补充更正，不覆盖原报告。

