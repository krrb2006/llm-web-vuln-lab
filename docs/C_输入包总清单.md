# C 输入包总清单（S001–S024，冻结支撑文件）

> 维护人：C　冻结日期：2026-10-16　用途：汇总 24 例的输入包去向、包哈希、源码基线与会话状态，供 A/B/C/D 交叉核对。
> 说明：本文档只记录"输入包"层面事实，不写任何 `ground_truth`；真值始终隔离在 `truth_review.md` / `evidence/truth/` 与 D 证据中。

## 一、状态口径（先读）

| 状态 | 含义 |
|---|---|
| 已锁定 | 输入包已冻结且提交；源码自 D 最近证据后未再变更，无需重算包哈希。 |
| 待D重验 | 输入包已生成，但源码在 D 最近证据之后发生过异常处理/对齐变更，需 D 按新 `case_code_sha256` 复跑确认；复跑确认前包为"暂定"，确认后转"已锁定"。 |
| 待D对齐后出包 | 源码尚未按统一 `try/catch(Throwable)` 口径对齐，C 暂不产包，对齐后由 C 出正式包。 |

- `packet_sha256` 为 `code_input.txt` 的 LF 内容哈希（与 line_map.json 记录的 `packet_sha256` 及 git 提交后 blob 一致）。
- `源码基线提交` 为该样本 PHP 源码最后一次修改的提交；后续对齐会更新此值。
- `正式包版本目录` 相对 `dataset/packets/`。

## 二、24 包总清单

| sample_id | split | 家族 | 正式包版本目录 | packet_sha256 | 源码基线提交 | 状态 |
|---|---|---|---|---|---|---|
| S001 | dev | SQL01 | S001_v1 | `3a84669c84cee3841bf080bb546069a0367b152476cb163a47e533c6661437e1` | `6b522ea` | 待D重验 |
| S002 | dev | SQL01 | S002_v1 | `2a55ab105d2153549d248b39b40f22f7fdbbb3471133192ac46060a2ee1546a7` | `6b522ea` | 待D重验 |
| S003 | dev | SQL02 | S003_v1 | `965cfab7cf9654ff767f04f15a060994728d07226cf99346e1b64147d70a98ac` | `6b522ea` | 待D重验 |
| S004 | dev | SQL02 | S004_v1 | `9c6ca039383b371e799c7eaa34a2183d852c62bda00947e932c2392ef8032235` | `6b522ea` | 待D重验 |
| S005 | dev | SQL03 | S005_v1 | `b229827144f951e72a1f1851709487753473a0c92b34a85787db39a81bf48b5e` | `6b522ea` | 待D重验 |
| S006 | dev | SQL03 | S006_v1 | `86bbb4103876ae0b56ea28588ba7135eff8076028c87bf079b0455b6bab60bdb` | `6b522ea` | 待D重验 |
| S007 | test | SQL04 | S007_v1 | `0da0b54298c41a089e37c3e1857b02c1cd2124a121ae41f1eaad4ceb0e72861f` | `6b522ea` | 待D重验 |
| S008 | test | SQL04 | S008_v1 | `0b3a718318ce598616ff47aab0a25b110d8f9cd303378d2c20d941110db09dac` | `6b522ea` | 待D重验 |
| S009 | test | SQL05 | S009_v2 | `7a9dd6065e6bd074801d293c94520d93b3f71f7ece14d3244daad1f765f8a5c4` | `7e50925` | 已锁定 |
| S010 | test | SQL05 | S010_v2 | `1e32adc03620cfd699350fb5399083304cc75277420eba51697672374c06f58f` | `7e50925` | 已锁定 |
| S011 | test | SQL06 | S011_v2 | `5b38ba932707b693d705e8b54b2340a5e4b6e84cc68cf47210f9c3f77f9e5299` | `9d5a234` | 待D重验 |
| S012 | test | SQL06 | S012_v2 | `fde871dc44f3eff9841293555a58c7a9f62323306e9a64f91b4f8d3db2be0945` | `9d5a234` | 待D重验 |
| S013 | dev | XSS01 | S013_v1 | `154456e20c0d4adc6febf6945c6d14c2b97722a38746a4c7ae1fa87a24a6cb4f` | `d4f7147` | 已锁定 |
| S014 | dev | XSS01 | S014_v1 | `7e68e97273ddb20a30ce51c1f1ad1dc0fcb4bc30c248340e41296030cce59f03` | `d4f7147` | 已锁定 |
| S015 | dev | XSS02 | S015_v1 | `098b1cade9931f53f2be7437a16f595f75670deb944308a4e1c72f7b253077dc` | `d4f7147` | 已锁定 |
| S016 | dev | XSS02 | S016_v1 | `71dbcaaa311f580897e7b2109160e34db33614ad625d3287563fd278672eef24` | `d4f7147` | 已锁定 |
| S017 | dev | XSS03 | — | — | `a296e4b` | 待D对齐后出包 |
| S018 | dev | XSS03 | — | — | `a296e4b` | 待D对齐后出包 |
| S019 | test | XSS04 | S019_v1 | `4ee21e7ded087864991df5d86192e1291e222e410d040b83b1b37aa90b19d9ab` | `a296e4b` | 已锁定 |
| S020 | test | XSS04 | S020_v1 | `64ec2ee56ba873938292418f4342eb3c3233f181e7ed879c2caac4eaa38d953e` | `a296e4b` | 已锁定 |
| S021 | test | XSS05 | — | — | `a296e4b` | 待D对齐后出包 |
| S022 | test | XSS05 | — | — | `a296e4b` | 待D对齐后出包 |
| S023 | test | XSS06 | S023_v1 | `e47750fd9ff681dc105db0d409800d915a6dd5adfe41d452113e35680b4c3781` | `a296e4b` | 已锁定 |
| S024 | test | XSS06 | S024_v1 | `c78a31862f547c160a20fee6a84e09172afc8da441deed8ff543ad76783a109c` | `a296e4b` | 已锁定 |

## 三、待D重验明细（为什么是"暂定"）

| 样本 | 触发变更 | D 现有证据基线 | 需要 D 做的动作 |
|---|---|---|---|
| S001–S008 | `6b522ea`（A 严格异常处理修订：查询/取数套 `try/catch(Throwable)`，异常只写日志、页面普通提示） | 旧基线 `d498903` | 按新 `case_code_sha256` 复跑普通请求与语法错误请求，确认异常不回显、业务结论不变 |
| S011/S012 | `9d5a234`（SQL06 ORDER BY 对齐 try/catch，`case_code_sha256` 变化） | 旧提交 `a04a832` | 按新哈希确认运行文件一致并复跑参考请求 |

> 说明：以上变更均不改 SQL/XSS 的核心结论路径（拼接/绑定位置不变），只改异常隔离，故输入包仍按当前源码冻结；D 复跑确认后即可转"已锁定"。

## 四、无数据库样本的补充说明

- S019/S020（XSS04，控制器+模板）、S023/S024（XSS06，链接 href）无数据库、无登录、无会话。
- 其输入包已冻结（`a296e4b` 起源码未再变更），故标"已锁定"。
- 浏览器侧行为（S019/S020 的反射 marker、S023/S024 的"实际点击 href 才导航"）仍待 D 按常规流程首次实测记录；S023/S024 需注意"页面加载不执行 ≠ 安全"，须以实际点击后的浏览器行为为准。

## 五、来源分支与哈希取用记录

- S001–S006：`c/packets-s001-s006` 的 `dataset/packets/S00x_v1/line_map.json`
- S009–S016：`c/samples` 的 `line_map.json`（S009–S012 取 v2，S013–S016 取 v1）
- S019/S020/S023/S024：`c/packets-s017-s024` 的 `line_map.json`
- S007/S008：本分支 `c/packets-s007-s008` 新生成（见下）

## 六、本次（c/packets-s007-s008）新增与冻结范围

- 新增 `dataset/specs/S007.json`、`S008.json`；新增 `dataset/packets/S007_v1/`、`S008_v1/`。
- S007/S008 均为 `index.php`(F01) + `repository.php`(F02) 双文件入包，`common/db_connect.php` 不入片段（context 说明 `$db` 与 utf8mb4）。
- 不修改 `dataset/manifest.json`（`ground_truth` 保持 `null`，`case_code_sha256` 等来源字段以各样本 `source_note.md` 为准）。
