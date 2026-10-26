# ADV 本地动态验证复跑（2026-10-26）

执行人：A  
范围：仅本地教学靶场 `http://127.0.0.1:4280`；不访问外部目标。

## 可复现步骤

```powershell
python environment/build_advanced_cases.py --a-ref HEAD --c-ref HEAD --d-ref HEAD
python environment/init_lab_db.py --reset-advanced
docker compose --env-file local/lab.env -f third_party/DVWA/compose.yml -f environment/compose.lab.yml up -d
python environment/check_advanced.py --output results/ADV_runtime_recheck_2026-10-26.json --compose docker compose --env-file local/lab.env -f third_party/DVWA/compose.yml -f environment/compose.lab.yml
```

## 运行环境与观察

- Docker Engine：`29.8.2`。
- 服务：`dvwa-dvwa-1` 将容器 HTTP 80 端口仅发布为 `127.0.0.1:4280`；数据库端口未对主机发布。
- PHP 语法检查：6/6 通过。
- 二阶 SQLi：向漏洞版写入普通昵称与受控字符串后，漏洞版 `lookup_profile.php?id=4` 的响应长度为 33，修复版对应响应长度为 15；两者 SHA-256 不同，脚本判定 `vulnerable_response_longer_than_fixed`。
- IDOR：会话用户设为 101 时，漏洞版读取 `id=1002` 返回 `owner_id=202`；修复版对同一对象返回空响应。脚本判定 `vulnerable_allows_other_owner_fixed_filters_owner`。

机器可读原始观察在 `results/ADV_runtime_recheck_2026-10-26.json`，SHA-256：`3e87e41efacb51dafc6b117a3c9e536896f751b5d1339072fb131ca44291ed48`。

## 解释边界

这是用仓库受控脚本完成的本地动态对照，不是将 DeepSeek 给出的原始 POC 文本逐字执行：模型的二阶 SQLi POC 使用过时路径，而 IDOR POC 命令为空。模型回答中 `poc_execution` 仍应保持 `not_run`；本记录只证明教学靶场的相应漏洞/修复代码路径可复现。
