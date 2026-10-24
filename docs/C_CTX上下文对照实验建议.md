# C 上下文对照（CTX）实验建议书

> 提议人：C　日期：2026-10-16　用途：按《C_样本与预处理操作手册》第五节"两例上下文补充实验"给出两个 CTX 样本的选型与片段划分计划，供 A/B 在群内确认口径。
> 边界：本文只写方案，**不实际生成包、不跑模型、不填 manifest**。确认后再由 C 生成 CTX 包并交 B 以同一冻结 Prompt + 模型执行。

## 一、前提：开发集无真正跨文件样本

第五节要求"从开发集选择两个有跨文件条件的样本"。经逐目录核对，开发集（S001–S006、S013–S018）**全部为单文件**：

| 开发集 | 家族 | 文件构成 |
|---|---|---|
| S001–S006 | SQL01/02/03 | 仅 `index.php` |
| S013–S016 | XSS01/02 | 仅 `index.php` |
| S017/S018 | XSS03 | 仅 `index.php` |

即开发集不存在"入口 + 关联函数/模板"的跨文件条件，无法满足第五节要求。因此 CTX 样本必须取自 test 集，需 A/B 确认此口径偏离（第五节原文为"开发集"，但开发集结构不支持）。

## 二、选型建议：两个 CTX 样本

在 test 集的跨文件样本中，建议选取以下两个（一个 SQL 跨函数、一个 XSS 控制器+模板，覆盖两种跨文件模式）：

| CTX 编号 | 样本 | 家族 | 跨文件模式 | 为什么选它 |
|---|---|---|---|---|
| CTX-1 | S007/S008 | SQL04 | 跨**函数**：入口 `index.php` 调用 `repository.php` 的 `find_people_by_name()`，拼接/prepare 在 repository 内 | 入口可见"调用"，sink 在另一文件函数体，最能测"缺失上下文" |
| CTX-2 | S019/S020 | XSS04 | 控制器+模板：入口 `index.php` `require` `templates/preview.php`，输出编码在模板内 | 入口可见"require + 传参"，sink 在模板输出位 |

不选 S021/S022（XSS05）的原因：其为三文件草稿流且依赖数据库，当前处于"待 D 对齐"，不适合现在做 CTX。

## 三、每个样本的片段划分计划

> 约定：同一 CTX 内，"仅入口"与"入口+关联"使用**完全相同**的 `<runtime_context>`，唯一差异是 fragments 是否包含关联文件。这样模型输出的差异可归因于"是否补充关联文件"，而非 context 措辞变化。context 沿用对应正式包的 context（如 S007/S008 的 `lab_people` 三行虚构数据、无登录、无会话等）。

### CTX-1：SQL04 跨函数（S007 vulnerable / S008 fixed）

| 变体 | 片段划分 | 模型能看到 / 看不到 |
|---|---|---|
| S007 仅入口 | F01 = `index.php` 1–24 | 能看到 `require_once .../repository.php`(行6) 与 `find_people_by_name($db, $name)`(行11)；**看不到** repository 内的字符串拼接与 `$db->query` |
| S007 入口+关联 | F01 = `index.php` 1–24 + F02 = `repository.php` 1–9 | 完整链路：入口取参 → 调用 → 拼接(行7) → 执行(行8) |
| S008 仅入口 | F01 = `index.php` 1–24 | 同上；**看不到** repository 内的 prepare/bind |
| S008 入口+关联 | F01 = `index.php` 1–24 + F02 = `repository.php` 1–13 | 完整链路：入口取参 → 调用 → prepare(行7)/bind(行8)/execute(行9) |

- "入口+关联"两个变体即正式包 S007_v1 / S008_v1；"仅入口"为 CTX 专用，不并入正式集。
- 关键观察点：仅入口时模型能否在看不到 repository 函数体的情况下给出正确判定，或是否给出"无法定位/需补充 repository"的说明。

### CTX-2：XSS04 控制器+模板（S019 vulnerable / S020 fixed）

| 变体 | 片段划分 | 模型能看到 / 看不到 |
|---|---|---|
| S019 仅入口 | F01 = `index.php` 1–8 | 能看到 `$_POST['content']` 赋值(行5) 与 `require .../templates/preview.php`(行8)；**看不到** 模板内 `echo $content` |
| S019 入口+关联 | F01 = `index.php` 1–8 + F02 = `templates/preview.php` 1–19 | 完整链路：入口取参 → require 模板 → 模板输出位(行16) |
| S020 仅入口 | F01 = `index.php` 1–8 | 同上；**看不到** 模板内 `htmlspecialchars` |
| S020 入口+关联 | F01 = `index.php` 1–8 + F02 = `templates/preview.php` 1–19 | 完整链路：入口取参 → require 模板 → 模板输出位(行16) |

- 同样，"入口+关联"即正式包 S019_v1 / S020_v1。
- 关键观察点：仅入口时模型能否意识到"输出在未提供的模板内"，从而避免仅凭入口（无 sink）误判。

## 四、执行与记录口径（待 A/B 确认后执行）

1. 实验编号：CTX-1（SQL04）、CTX-2（XSS04）；每个 CTX 下 4 个输入（2 样本 × 仅入口/入口+关联）。
2. 同一冻结 Prompt、同一模型、同一 context；仅 fragments 不同。
3. 记录两输入的**精确差异**（片段清单），不把 CTX 结果并入正式集；不把"给 V2 补函数后的收益"单独归因于 Prompt。
4. 若"仅入口"无法判定，同样作为结论记录——它本身就是"完整上下文必要性"的证据。
5. 真值验证两者一致（S007/S008 均以 D 复跑 `lab_people` 条件变化为准；S019/S020 均以浏览器 marker 为准），不得仅凭文件哈希不同说明行为改变。

## 五、待确认项（请在群内与 A/B 对齐）

1. 是否接受"开发集无跨文件、CTX 改取 test 集 S007/S008、S019/S020"这一口径偏离。
2. "仅入口"变体是否保持与正式包完全相同的 context（本方案采用"相同 context、仅减片段"）。
3. 是否需要在 CTX 包目录使用独立命名（如 `dataset/packets/CTX-S007A_entryonly_v1/`）以免与正式 `S007_v1` 混淆。
