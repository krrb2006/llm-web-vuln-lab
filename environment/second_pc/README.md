# 第二台电脑复现记录（A 执行）

- 执行人：A
- 执行时间：2026-10-20 22:07（Asia/Shanghai）
- 机器：Windows 11 家庭中文版
- 仓库提交：`34b36ad2aeeb8be2a6fe3562fbe0f40d532fad5e`
- Python 3.11.15（说明要求 3.12；版本差异已记录，不改脚本）
- Docker Engine 29.8.2 / Compose 5.5.1；DVWA PHP 8.5.11；MariaDB 10.11.19；Edge 155.0.4283.45
- `check_runtime` 37/37；S009 1→3 行；S011 排序变化通过；S017–S024 业务检查通过；S021 marker=yes、S022 无 marker
- 未运行模型、未运行 POC、未修改 `runs/formal.json`

## 文件

- `version_second_pc_A.txt`、`services_second_pc_A.txt`、`runtime_check_second_pc_A.json`：A 机器上的原始记录
- `environment/second_pc_commit.txt`：A 使用的仓库提交

## 限制

- 本次未生成新的屏幕截图和 60–90 秒录屏；A 在 `results/A_second_pc_repro_2026-10-20.md` 中如实注明，未用 D 的旧截图冒充。
- Python 3.11.15 与说明的 3.12 有 minor 差异；本次 build/check 脚本均通过，未发现行为差异。

## 与主环境文件的关系

`environment/version.txt`、`services.txt`、`runtime_check.json` 是 **D 第一台电脑**的冻结基线，已恢复；A 的第二台机器数据只放在本目录，避免覆盖主环境记录。
