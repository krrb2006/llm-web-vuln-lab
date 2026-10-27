# D 独立复核补充：A 的 POC 可执行性（2026-10-19）

复核人：D　复核对象：A 的 S007/S021 六条 `poc_generated=true` 记录
说明：A 的 9 条正式记录目前没有 `pocs/F_*/original.py`。D 从 `runs/F_*/raw_output.txt` 的 Python 代码块中提取原文，放在本目录下做**独立复核**，不修改 A 的 `pocs/` 或 `runs/formal.json`。

## 一、S007（SQLi，vulnerable）

在冻结源码 `6cd58b3` 的本地靶场上直接运行提取出的原脚本（未改代码）：

| run_id | exit | 观察 |
|---|---|---|
| F_S007_V0_R1 | 0 | 普通 `name=Alice` 返回 ID 1；`Alice' AND '1'='2` 无结果，条件变化 |
| F_S007_V1_R1 | 0 | 测试输入返回 Alice/Bob/Carol 三行，普通输入不返回全部 |
| F_S007_V2_R1 | 0 | 普通 1 行；测试输入返回 3 行，条件变化 |

- 三条 POC 都只 GET `127.0.0.1:4280/lab_cases/S007/index.php`，无外发、无写操作、无 Cookie。
- 结论：A 的 S007 POC 原文可执行，且能在本地复现条件变化；A 仍应把原脚本归档到 `pocs/F_S007_*/original.py`，并把上述执行结果写入自己的 verification。

## 二、S021（XSS，vulnerable）

- 三条 POC 都是提交脚本：要求 `--submit-url` 与 `--case {normal,test}`，只 POST 到 `127.0.0.1:4280`，marker 只插入页面节点，不读 Cookie、不发外部请求。
- 脚本本身**不跟随重定向、不断言 JavaScript 执行**，执行后需人工在浏览器打开 `preview_url` 观察 marker；因此仅运行脚本不能证明 XSS 触发。
- D 未执行这三条（避免在 A 的正式记录之外留下未归档数据）；静态审阅通过，目标约束安全。
- A 需要：归档 `pocs/F_S021_*/original.py`，在浏览器完成 marker 观察，并按 `templates/verification.md` 记录 `verification=triggered/not_triggered`。

## 三、对 PR #10 结论的影响

- “POC 原文缺失”这一项仍成立：A 的正式记录里没有 `pocs/` 文件；D 的提取件只是复核材料。
- “POC 是否可执行”这一项对 S007 已由 D 独立确认；S021 需浏览器执行，仍待 A 补。
- PR #10 的结论保持 **有条件通过**：判定/定位通过；证据完整性待 A 补 POC 原文、截图与 metadata 快照。

## 四、证据

- 提取脚本与日志：`results/D_review_A_pocs/F_S007_V0_R1.py`、`.stdout.txt`、`.stderr.txt`、`.exit.txt`（V1/V2 同）。
- S021 提取脚本：`results/D_review_A_pocs/F_S021_V0_R1.py`、`V1`、`V2`（未执行）。
