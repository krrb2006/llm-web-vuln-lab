# ADV 环境接线与运行状态（2026-10-25）

## 已完成的环境接线

- `environment/build_advanced_cases.py`：将两组漏洞版/修复版复制到本地只读靶场，修正运行副本的数据库 include，并提供 `$conn = $db` 兼容别名。
- `environment/init_lab_db.py --reset-advanced`：创建并初始化 `profiles`、`invoices`，写入用户 A/B 对照发票，并授予教学数据库最小权限。
- `environment/build_advanced_cases.py` 生成本地 IDOR 测试 session 入口；仅用于 `127.0.0.1:4280` 的本地对照。
- `environment/check_advanced.py`：执行 PHP 语法检查、二次 SQLi 的普通/受控跨请求对照，以及 IDOR 自有对象/他人对象对照。

## 当前运行阻塞

本机 Docker daemon 当前未启动，Docker API 返回 `dockerDesktopLinuxEngine` named pipe 不存在。因此本轮只完成了脚本语法检查和运行副本构建，尚未执行：

- PHP lint；
- HTTP 正常业务回归；
- 二次 SQLi 漏洞/修复对照；
- IDOR 越权/修复对照。

ADV 四条仍保持 `planned`，没有生成正式运行记录，也没有声称漏洞触发。

## Docker 启动后的执行顺序

```powershell
python environment/build_advanced_cases.py
python environment/init_lab_db.py --reset-advanced
docker compose --env-file local/lab.env -f third_party/DVWA/compose.yml -f environment/compose.lab.yml up -d
python environment/check_advanced.py --compose docker compose --env-file local/lab.env -f third_party/DVWA/compose.yml -f environment/compose.lab.yml
```

完成后由 D 独立复核六个 PHP 文件、普通业务输出、二次 SQLi 对照和 IDOR 会话对照，再由 A 生成四条模型运行记录并决定状态。
