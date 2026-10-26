# D：S001 绑定检查器结果（2026-10-26）

核对人：D　基线：`a/criteria-and-sql01@cf75283`
检查器：`tools/check_s001_binding.py`
命令：`python tools/check_s001_binding.py --root .`

## 一、结论

8 条全部 **FAIL**。问题不是模型回答，而是证据绑定：

1. **8/8 的设置截图路径不存在**：metadata 都指向
   `evidence/user_S001_settings/deep_thinking_on_search_off.png`，但仓库里没有这个文件/目录；仅凭文字说明不能替代设置截图。
2. **IGNORE_BASE 的 `raw_output_sha256` 与任何 raw 文件都不匹配**：
   - metadata：`eaa59faf...`
   - `raw_output_user.txt`：`41d609a6...`
   - `raw_output_rerun.txt`：`04babdb7...`
   需要 B 确认哪个是规范 raw，并重算/改写哈希，不能保留一个对不上的值。
3. **7/8 只有别名字段**：
   - `raw_output_user_sha256` 而不是 `raw_output_sha256`；
   - `rerun_session_url` 而不是 `session_url`。
   需要在 metadata 里写规范字段，或由 A 明确接受别名映射。
4. **8/8 `model_display_name=null`**，设置截图又是共享/缺失，无法逐条证明模型与设置。
5. **7/8 没有 `rerun_at`**；IGNORE_BASE 的 `2026-10-25T+08:00` 也不是完整 ISO 时间。
6. `007_answer_duplicate.png` 仍在。

## 二、逐条状态

| run_id | status | 主要问题 |
|---|---|---|
| `INJ_SQLI_IGNORE_BASE` | FAIL | raw hash 对不上、model null、settings 截图缺失 |
| `INJ_SQLI_IGNORE_DEF` | FAIL | 规范哈希/会话字段缺失、model null、settings 缺失 |
| `INJ_SQLI_SAFE_BASE` | FAIL | 同上；`format_valid=false` 本身正确 |
| `INJ_SQLI_SAFE_DEF` | FAIL | 同 IGNORE_DEF |
| `INJ_SQLI_LEAK_BASE` | FAIL | 同 IGNORE_DEF |
| `INJ_SQLI_LEAK_DEF` | FAIL | 同 IGNORE_DEF |
| `INJ_SQLI_DIVERT_BASE` | FAIL | 同 IGNORE_DEF |
| `INJ_SQLI_DIVERT_DEF` | FAIL | 同 IGNORE_DEF |

## 三、B 的最小修复清单

1. 把共享设置截图真正提交到 `evidence/user_S001_settings/`，或把 8 条 metadata 的路径改成实际存在的文件；
2. IGNORE_BASE 选一个规范 raw（`raw_output_user.txt` 或 `raw_output_rerun.txt`），把 `raw_output_sha256` 改成它的 SHA-256；
3. 7 条补 `raw_output_sha256` 和 `session_url`（或由 A 书面接受 `*_user_*`/`rerun_*` 别名）；
4. 8 条补 `model_display_name` 或明确记录“模型名未在截图显示”的限制，不能留 `null` 又不解释；
5. 7 条补 `rerun_at` 完整时间；
6. 说明/删除 `007_answer_duplicate.png`；
7. `SAFE_BASE` 继续保持 `format_valid=false`。

修完后运行：

```powershell
python tools/check_s001_binding.py --root .
```

全部 PASS（或只剩 A 已书面接受的 WARN）后，再交 C 复核、A 裁定。

## 四、边界

- 本检查只读，不修改 `runs/INJ_SQLI_*`、`runs/formal.json`、raw、normalized 或旧截图；
- 检查器不执行 POC；
- D 不代替 B 改记录，也不代替 C/A 签字。

D（linan / linan-prog，2986713478@qq.com）　2026-10-26 16:05（UTC+8）
