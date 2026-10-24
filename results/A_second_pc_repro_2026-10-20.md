# A 侧第二台电脑复现报告

执行人：A

执行时间：2026-10-20 22:07（Asia/Shanghai）

说明：D 的复现在 D 的电脑完成；本次在 A 的另一台 Windows 工作机完成，因此本报告作为相对于 D 环境的第二台电脑复现。此次不运行模型、不运行 POC、不修改 `runs/formal.json`。

## 固定版本与环境

- A/C/D source commit：`34b36ad2aeeb8be2a6fe3562fbe0f40d532fad5e`
- OS：Windows 11 家庭版中文版
- Python：3.11.15（说明要求 3.12，版本差异已记录）
- Docker Engine：29.8.2；Docker Compose：5.5.1
- DVWA PHP：8.5.11；MariaDB：10.11.19-MariaDB-ubu2204
- Edge：155.0.4283.45
- 绑定：`127.0.0.1:4280`
- DVWA/MariaDB 镜像使用仓库 compose 中记录的 digest；未映射公网。

## 自动检查结果

- `build_lab_cases.py`：37 个 PHP 文件验证通过，运行树源码哈希与容器哈希一致。
- `check_runtime.py`：37/37，`failed=0`，无 unexpected runtime files，DVWA 配置通过。
- `check_sql_http.py`：S009 正常请求 1 行，受控条件 3 行；S011 正常/受控排序变化通过。
- `check_d_business.py`：S017–S024 业务请求全部完成，无 Fatal。
- `check_d_browser.mjs`：S021 preview 的 `document.documentElement.dataset.labXss` 为 `yes`；S022 无该属性；8 个样本观察文件已生成用于本机检查。
- `capture_environment.py`：DVWA login HTTP 200，官方 `low.php` 哈希匹配。

## 留证边界

本报告对应的 `environment/second_pc_commit.txt`、`runtime_check.json`、`version.txt`、`services.txt` 和脱敏 Compose 配置已保存。当前没有新增正式模型记录或 POC 记录。

自动浏览器检查已确认 S021/S022 的 DOM 结果，但本次没有生成新的屏幕截图和 60–90 秒录屏；因此不声称这些留证项已完成，也不使用 D 的旧截图替代。若课程硬性要求截图/录屏，由 A 在本机补录后再追加，不改变正式实验数据。
