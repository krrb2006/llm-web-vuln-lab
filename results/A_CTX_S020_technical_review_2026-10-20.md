# A 对 CTX S020 的技术复核记录

日期：2026-10-20（Asia/Shanghai）  
范围：`CTX_S020_ENTRY`、`CTX_S020_FULL`；不覆盖原始输出，不执行模型生成的 POC。

## 核对结果

|项目|ENTRY|FULL|
|---|---|---|
|样本类型|S020 / XSS|S020 / XSS|
|Prompt|XSS_V2，SHA-256=`3666ebeb28980e192172852639ab1759c94b6cbb2e5cdfe0c6f185a946841178`|同左|
|输入与 metadata 哈希|一致|一致|
|原文与 metadata 哈希|一致|一致|
|JSON 格式|`format_valid=true`|`format_valid=true`|
|模型预测|`uncertain`|`safe`|
|POC|未生成|未生成|

ENTRY 只提供入口片段，缺少 `templates/preview.php`，模型将结论保持为 `uncertain`；FULL 包含两个实际输出点并识别到 `htmlspecialchars` 转义，结论为 `safe`。两条输入除上下文范围外符合消融设计，观察到的变化可解释为完整模板信息带来的判断收窄。

## 状态边界

上述是 A 侧对仓库证据、哈希和格式的技术复核，不等同于浏览器执行验证。两条记录的 `human_verification` 仍保持 `pending`，未改写为 `reviewed`；CTX 不进入 36 条正式统计。

## 工具修复

已修正 `tools/prepare_context_ablation.py` 与 `tools/record_context_ablation.py` 的类型硬编码：S007 使用 `SQLi_V2`，S020 使用 `XSS_V2`。修复只影响后续输入准备和规范化校验，不修改旧 CTX 原文或旧规范化结果。
