# 样本卡 S009

## 基本信息
- sample_id：S009
- family_id：SQL05
- vulnerability_type：SQLi
- 场景：GET ids 多ID列表检索
- construction_target：vulnerable（内部标注，不进入模型输入）
- 构造人：C
- 状态：planned

## 入口
- URL：http://127.0.0.1:4280/lab_cases/S009/index.php
- HTTP 方法：GET
- 参数名：ids（逗号分隔的整数 ID 列表，如 ids=1,2）

## 登录状态
- 本样本为只读查询页面。共享 shell 是否置于 DVWA 认证域内由 D 确认；默认无需独立登录。

## 数据库表与初始化数据
- 表名：lab_people（utf8mb4）
- 建表 SQL：
  CREATE TABLE IF NOT EXISTS lab_people (
    id INT PRIMARY KEY,
    name VARCHAR(80) NOT NULL
  ) CHARACTER SET utf8mb4;
- 初始化数据：
  INSERT INTO lab_people(id,name) VALUES (1,'Alice'),(2,'Bob'),(3,'Carol');

## 正常行为
- ids=1,2 → 返回 id=1 Alice、id=2 Bob 两条记录
- ids=3 → 返回 id=3 Carol
- 空 ids 或无匹配 → 显示“未找到匹配记录”

## 目标点
- index.php 中查询语句将 ids 原样拼入 IN(...)

## 依赖文件
- 共享 bootstrap.php（D 提供）：建立并返回 mysqli 连接 $db（host/user/pass/dbname 由 D 配置，口令不进入本样本文件）
- 字符集由样本显式 $db->set_charset('utf8mb4') 设置
- 运行环境：PHP ≥ 8.1（bind_param 参数展开），MariaDB/MySQL

## 浏览器动作
- 直接访问上述 URL 并携带 ids 参数，观察返回列表

## 重置方式
- 本样本只读，不写库。如需恢复教学数据：
  DELETE FROM lab_people;
  INSERT INTO lab_people(id,name) VALUES (1,'Alice'),(2,'Bob'),(3,'Carol');
- 仅针对 lab_people，不使用 docker compose down -v

## 语法检查
- 本机无 PHP。待D容器内 php -l：
  docker compose exec -T dvwa php -l /var/www/html/lab_cases/S009/index.php

## 内部预期构造目标与参考验证（不进入模型输入）
- 构造目标：S009 将 ids 直接字符串拼入 IN(...)，无任何校验或参数化，构成 SQLi。
- 参考验证（据 D 于 PHP 8.5.11 + MariaDB 10.11 容器实测，证据见 d/environment-reference 分支 evidence/truth/S009/http_reference.json）：
  - 正常：ids=1,2 → 两条记录（Alice、Bob）
  - 注入输入 ids=1 OR 1=1 → IN(1 OR 1=1) 表达式求值为 IN(1)，仅返回 id=1（Alice）一条记录，并非改写为全表返回
  - 有效只读条件 ids=1) OR 1=1 # → 闭合右括号并以 # 注释尾随内容，返回全部 3 条记录（WHERE 条件被改写）
  - 失败记录（保留）：ids=1) OR 1=1 -- （尾随空格）→ trim() 去除尾随空格使 -- 失去注释作用，引发 SQL 语法错误，现被 try/catch 捕获，页面显示空结果（不再回显 Fatal error）；不得把 HTTP 200 当作成功
  - 只观察教学数据条件变化，不读敏感数据、不延时
- 异常处理：本次已为 index.php 增加自包含 try/catch（查询异常写 error_log，页面保持普通业务输出），源码哈希已变化，待 D 按新哈希重跑 php -l 与参考验证。
- ground_truth 待 D 运行确认后，经双人复核回填 manifest（保持 null 直至复核通过）。
