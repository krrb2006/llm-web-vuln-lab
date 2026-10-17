# A 给 C：S001–S008 真值复核清单

> 用途：C 复核 A 对 S001–S008（SQL01–SQL04）的真值标注。按项目分工，C 复核 A 的 8 例。
> 时机：在 A 完成初审、D 完成参考验证之后进行。真值必须来自「代码分析 + 参考验证」，不能取自模型回答。

## 一、复核对象

`dataset/raw/S001/` 到 `S008/`，每例含：`index.php`（S007/S008 另含 `repository.php`）、
`sample_card.md`、`source_note.md`、`truth_review.md`。

## 二、复核四步（对应 A 手册真值审核步骤）

1. **看卡与源码**：打开 sample_card 与源码，核对入口 URL/参数、依赖文件、输出位置、配对关系。
   若 A 只给了一个函数但调用者有关键过滤，要求 A 补齐。
2. **对证据**：对照 D 的参考验证（普通请求 + 受控输入），确认 ground_truth 结论与现象一致。
3. **查配对**：vuln/fixed 两例必须「正常业务一致、返回字段一致、输出编码一致」，唯一差异是目标缺陷；不得靠破坏功能制造「安全」。
4. **判口径**：结论只允许「满足/不满足/未知」，依据 `docs/judgment_criteria.md` 的 SQLi 四项检查逐条落地。

## 三、争议处理

争议先归为四类之一：代码上下文不足 / 运行与源码不一致 / 参考验证不充分 / 目标范围不一致。
在 `truth_review.md` 的「争议与解决记录」中记录提出人、原因归类、补充证据、最终结论；
仍无法一致则该样本 `ground_truth` 保持 `null`，不得凭投票取值。

## 四、复核产出

- 同意：在 `truth_review.md` 填「复核人及日期 = C」，随后由 A 在 `dataset/manifest.json` 写入
  `ground_truth`、`truth_reviewer = C`、`truth_evidence`，`status` 改 `ready`。
- 不同意/待定：记录争议，`ground_truth` 保持 `null`。

## 五、提醒

- `construction_target`（vulnerable/fixed）只是构造目标，不进入真实评分。
- `truth_review.md`、`sample_card.md` 等内部卡片不得发送给被评估模型。
