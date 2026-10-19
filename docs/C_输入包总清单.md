# C 输入包总清单（S001–S024，冻结支撑文件）

> 维护人：C　更新日期：2026-10-19　用途：汇总 24 例的输入包去向、包哈希、源码基线（A 分支提交）与会话状态，供 A/B/C/D 交叉核对。
> 说明：本文档只记录"输入包"层面事实，不写任何 `ground_truth`；真值始终隔离在 `truth_review.md` / `evidence/truth/` 与 D 证据中。

## 〇、本轮结论（先读）

- 24 例输入包已全部完成，且均已合入 A 分支 `origin/a/criteria-and-sql01`（HEAD `173b9af`）。
- 其中 **6 例动态证据待 D 复跑**：S011、S012、S017、S018、S021、S022。A 已声明这 6 例的源码变更（异常隔离对齐）**对真值不阻塞**。
- 本清单同时收录 CTX 上下文消融变体（附录七），CTX 不进入 36 条主实验。

## 一、状态口径（先读）

| 状态 | 含义 |
|---|---|
| 已锁定 | 输入包已冻结且提交；源码自 D 最近证据后未再变更，无需重算包哈希。 |
| 待D复跑 | 输入包已生成，但源码在 D 最近证据之后发生过异常处理/对齐变更，需 D 按新 `case_code_sha256` 复跑确认；复跑确认前包为"暂定"，确认后转"已锁定"。 |
| 待D对齐后出包 | 源码尚未按统一 `try/catch(Throwable)` 口径对齐，C 暂不产包，对齐后由 C 出正式包。 |

- `packet_sha256` 为 `code_input.txt` 的 LF 内容哈希（与 line_map.json 记录的 `packet_sha256` 及 git 提交后 blob 一致）。
- `case_code_sha256`：单文件样本取该 PHP 文件的 UTF-8/LF SHA-256；多文件样本按相对路径排序，将每行 `相对路径<TAB>文件SHA256\n` 拼接后再计算 SHA-256。
- `源码基线提交` 为该样本 PHP 源码在 **A 分支**最后一次修改的提交；原 c/samples、d/environment-reference 等分支提交经 A 变基集成后哈希变化，源码内容与 `case_code_sha256` 不变。
- `正式包版本目录` 相对 `dataset/packets/`。

## 二、24 包总清单

| sample_id | split | 家族 | 正式包版本目录 | packet_sha256 | 源码基线提交（A） | C 复核 | 状态 |
|---|---|---|---|---|---|---|---|
| S001 | dev | SQL01 | S001_v1 | `3a84669c84cee3841bf080bb546069a0367b152476cb163a47e533c6661437e1` | `6b522ea` | 已复核 | 已锁定 |
| S002 | dev | SQL01 | S002_v1 | `2a55ab105d2153549d248b39b40f22f7fdbbb3471133192ac46060a2ee1546a7` | `6b522ea` | 已复核 | 已锁定 |
| S003 | dev | SQL02 | S003_v1 | `965cfab7cf9654ff767f04f15a060994728d07226cf99346e1b64147d70a98ac` | `6b522ea` | 已复核 | 已锁定 |
| S004 | dev | SQL02 | S004_v1 | `9c6ca039383b371e799c7eaa34a2183d852c62bda00947e932c2392ef8032235` | `6b522ea` | 已复核 | 已锁定 |
| S005 | dev | SQL03 | S005_v1 | `b229827144f951e72a1f1851709487753473a0c92b34a85787db39a81bf48b5e` | `6b522ea` | 已复核 | 已锁定 |
| S006 | dev | SQL03 | S006_v1 | `86bbb4103876ae0b56ea28588ba7135eff8076028c87bf079b0455b6bab60bdb` | `6b522ea` | 已复核 | 已锁定 |
| S007 | test | SQL04 | S007_v1 | `0da0b54298c41a089e37c3e1857b02c1cd2124a121ae41f1eaad4ceb0e72861f` | `6b522ea` | 已复核 | 已锁定 |
| S008 | test | SQL04 | S008_v1 | `0b3a718318ce598616ff47aab0a25b110d8f9cd303378d2c20d941110db09dac` | `6b522ea` | 已复核 | 已锁定 |
| S009 | test | SQL05 | S009_v2 | `7a9dd6065e6bd074801d293c94520d93b3f71f7ece14d3244daad1f765f8a5c4` | `521cc77` | 已复核 | 已锁定 |
| S010 | test | SQL05 | S010_v2 | `1e32adc03620cfd699350fb5399083304cc75277420eba51697672374c06f58f` | `521cc77` | 已复核 | 已锁定 |
| S011 | test | SQL06 | S011_v2 | `5b38ba932707b693d705e8b54b2340a5e4b6e84cc68cf47210f9c3f77f9e5299` | `881bc3b` | 已复核（LF 修复） | 待D复跑 |
| S012 | test | SQL06 | S012_v2 | `fde871dc44f3eff9841293555a58c7a9f62323306e9a64f91b4f8d3db2be0945` | `881bc3b` | 已复核（LF 修复） | 待D复跑 |
| S013 | dev | XSS01 | S013_v1 | `154456e20c0d4adc6febf6945c6d14c2b97722a38746a4c7ae1fa87a24a6cb4f` | `4c6383b` | 已复核 | 已锁定 |
| S014 | dev | XSS01 | S014_v1 | `7e68e97273ddb20a30ce51c1f1ad1dc0fcb4bc30c248340e41296030cce59f03` | `4c6383b` | 已复核 | 已锁定 |
| S015 | dev | XSS02 | S015_v1 | `098b1cade9931f53f2be7437a16f595f75670deb944308a4e1c72f7b253077dc` | `4c6383b` | 已复核 | 已锁定 |
| S016 | dev | XSS02 | S016_v1 | `71dbcaaa311f580897e7b2109160e34db33614ad625d3287563fd278672eef24` | `4c6383b` | 已复核 | 已锁定 |
| S017 | dev | XSS03 | S017_v1 | `81f3c30168c5012ee06ce8a4adb6ba0930ac20dfab5e8170cc8862fbe94980f8` | `f82ddc2` | 本轮通过 | 待D复跑 |
| S018 | dev | XSS03 | S018_v1 | `0daa5625730551f204c738eea7b9c23e3a31c5bbd0efff23e94535e006e6c350` | `f82ddc2` | 本轮通过 | 待D复跑 |
| S019 | test | XSS04 | S019_v1 | `4ee21e7ded087864991df5d86192e1291e222e410d040b83b1b37aa90b19d9ab` | `0f3062a` | 已复核 | 已锁定 |
| S020 | test | XSS04 | S020_v1 | `64ec2ee56ba873938292418f4342eb3c3233f181e7ed879c2caac4eaa38d953e` | `0f3062a` | 已复核 | 已锁定 |
| S021 | test | XSS05 | S021_v1 | `e881e86713926107fa7db458b38c0e9fc824f5a8d916e2ebb799833e7e7122a5` | `f82ddc2` | 本轮通过 | 待D复跑 |
| S022 | test | XSS05 | S022_v1 | `ccf37ff8d9b045f365659a9c66896b669cbd6e5b424defd56c5e385b86bba5bd` | `f82ddc2` | 本轮通过 | 待D复跑 |
| S023 | test | XSS06 | S023_v1 | `e47750fd9ff681dc105db0d409800d915a6dd5adfe41d452113e35680b4c3781` | `0f3062a` | 已复核 | 已锁定 |
| S024 | test | XSS06 | S024_v1 | `c78a31862f547c160a20fee6a84e09172afc8da441deed8ff543ad76783a109c` | `0f3062a` | 已复核 | 已锁定 |

## 三、待D复跑明细（6 例，A 已声明对真值不阻塞）

| 样本 | 触发变更 | D 现有证据基线 | 需要 D 做的动作 |
|---|---|---|---|
| S011/S012 | `881bc3b`（SQL06 ORDER BY 查询/取数套 `try/catch(Throwable)`，`case_code_sha256` 变化） | 旧提交 `a04a832` | 按新哈希确认运行文件一致并复跑参考请求 |
| S017/S018 | `f82ddc2`（A 按统一口径补齐写入和读取全流程 `try/catch(Throwable)`） | D 旧基线 `a296e4b` | 部署新源码，复跑普通留言、受控XSS及数据库异常，确认错误不回显 |
| S021/S022 | `f82ddc2`（A 按统一口径补齐 submit/list/preview 数据库流程异常隔离） | D 旧基线 `a296e4b` | 复跑三页面业务、存储XSS与数据库异常，确认页面仅普通提示 |

> 说明：以上 6 例变更均不改 SQL/XSS 的核心结论路径（拼接/绑定位置不变），只改异常隔离，故输入包仍按当前源码冻结；A 已声明对真值不阻塞，D 复跑确认后即可转"已锁定"。

> 另注：S001–S008 的 `6b522ea` 严格异常处理修订已完成静态复核并合入，其"异常不回显页面"的容器级复验属于已跟踪的收尾项（A 真值复核已按 `6b522ea` 口径归档核心结论，不阻塞）；不在本轮 6 例动态证据范围内。

## 四、无数据库样本的补充说明

- S019/S020（XSS04，控制器+模板）、S023/S024（XSS06，链接 href）无数据库、无登录、无会话。
- 其输入包已冻结（源码未再变更），故标"已锁定"。
- 浏览器侧行为（S019/S020 的反射 marker、S023/S024 的"实际点击 href 才导航"）仍待 D 按常规流程首次实测记录；S023/S024 需注意"页面加载不执行 ≠ 安全"，须以实际点击后的浏览器行为为准。

## 五、来源分支与哈希取用记录（A 分支集成后）

- 24 包均已合入 `origin/a/criteria-and-sql01`；`packet_sha256` 与 `line_map.json`、`code_input.txt` LF 内容三端一致（C 已复核）。
- 源码基线提交以 A 分支 `git log -1 -- dataset/raw/<sid>/*.php` 为准；原分支提交对应关系（同内容、变基后哈希变化）：
  - S009/S010：原 `7e50925` → A `521cc77`；
  - S011/S012：原 `9d5a234` → A `881bc3b`（LF 口径源码哈希 `files[].sha256` 已统一为 LF）；
  - S013–S016：原 `d4f7147` → A `4c6383b`；
  - S019/S020/S023/S024：原 `a296e4b` → A `0f3062a`。
- S009–S012 的旧 v1 包已移至 `dataset/archive/packets/`，只保留审计历史，不参与冻结扫描。

## 六、本轮（c/review-s017-s022）复核范围

- 逐行复核 S017/S018/S021/S022 四个 v1 包：片段行号、异常处理（try/catch(Throwable)、异常仅 `error_log()`、读取失败回退空数组/null）、配对差异（仅目标缺陷行）、`files[].sha256`=LF 源码哈希、`packet_sha256` 重算、无答案词泄露，全部通过。
- 复核 S011/S012 v2 的 `files[].sha256` 已为 LF 口径（`3028eb9c…` / `08a09dcc…`），`packet_sha256` 不变；S009/S010 v2 不受影响。
- 详见 `docs/C_S017-S022四包复核报告.md`。

## 七、附录：CTX 上下文消融变体

CTX 按 A 裁定（`docs/A_新反馈整合裁定_2026-10-17.md` 第五节）仅取 S007、S020，各做 entry-only 与 full-context 两种输入，共 4 条；编号与 `experiments/bonus_runs.plan.json` 一致（category=`context_ablation`，operator=C，reviewer=A，status=planned，prompt_version=V2）。**CTX 不进入 36 条主实验，且须待 36 条主实验原始输出归档后才执行。**

| run_id | sample_id | 输入变体 | 输入包来源 | packet_sha256 |
|---|---|---|---|---|
| CTX_S007_ENTRY | S007 | entry-only（仅 index.php，缺 repository.php） | `experiments/context_ablation/CTX_S007_ENTRY/` | `ab7a9ad4c5fd4125b194f306582135be58629da621ba556d020a3ec02efee29b` |
| CTX_S007_FULL | S007 | full-context（复用正式包） | `dataset/packets/S007_v1/` | `0da0b54298c41a089e37c3e1857b02c1cd2124a121ae41f1eaad4ceb0e72861f` |
| CTX_S020_ENTRY | S020 | entry-only（仅 index.php，缺 templates/preview.php） | `experiments/context_ablation/CTX_S020_ENTRY/` | `1c8ba697fef233678f9b47b044f47e6fed9f5c9df2f25eb50486bdac93aafc67` |
| CTX_S020_FULL | S020 | full-context（复用正式包） | `dataset/packets/S020_v1/` | `64ec2ee56ba873938292418f4342eb3c3233f181e7ed879c2caac4eaa38d953e` |

- entry-only 变体与正式包共用同一 `<runtime_context>` 文本，唯一差异是 fragments 只保留入口文件（F02 缺失）；`files[].sha256` 采用 LF 口径，`packet_sha256` 为 LF 内容哈希。
- entry-only 变体存放于 `experiments/context_ablation/`（**不在** `dataset/packets/`，避免 `check_freeze.py` 把 S007/S020 判成"一例对应两个正式包"）。
- 两种输入共用同一冻结 Prompt（V2）、模型设置与 runtime context；本清单只登记输入变体，不填写任何运行结果。
