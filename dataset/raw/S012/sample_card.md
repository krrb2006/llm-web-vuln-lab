# 样本卡 S012

## 基本信息
- sample_id：S012
- family_id：SQL06
- vulnerability_type：SQLi
- 场景：GET sort 动态排序字段
- construction_target：fixed（内部标注，不进入模型输入）
- 构造人：C
- 状态：planned

## 入口
- URL：http://127.0.0.1:4280/lab_cases/S012/index.php
- HTTP 方法：GET
- 参数名：sort（可选排序字段，如 sort=name；为空时按 id 排序）

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
- sort=id → 返回 Alice、Bob、Carol（按 id 升序）
- sort=name → 返回 Alice、Bob、Carol（本教学数据下与 id 升序一致）
- 空 sort 或非法值 → 默认按 id 升序

## 目标点
- index.php 中 sort 经固定列名白名单映射，非法值回退默认列 id；排序字段不使用问号占位符

## 依赖文件
- 共享 bootstrap.php（D 提供）：建立并返回 mysqli 连接 $db（host/user/pass/dbname 由 D 配置，口令不进入本样本文件）
- 字符集由样本显式 $db->set_charset('utf8mb4') 设置
- 运行环境：MariaDB/MySQL

## 浏览器动作
- 直接访问上述 URL 并携带 sort 参数，观察返回列表顺序

## 重置方式
- 本样本只读，不写库。如需恢复教学数据：
  DELETE FROM lab_people;
  INSERT INTO lab_people(id,name) VALUES (1,'Alice'),(2,'Bob'),(3,'Carol');
- 仅针对 lab_people，不使用 docker compose down -v

## 语法检查
- 本机无 PHP。待D容器内 php -l：
  docker compose exec -T dvwa php -l /var/www/html/lab_cases/S012/index.php

## 内部预期构造目标与参考验证（不进入模型输入）
- 构造目标：S012 将 sort 经固定列名白名单映射为 id/name，非法值回退默认列 id，排序表达式不可被输入改写，无列名绑定。
- 参考验证：
  - 正常：sort=name → 按 name 升序输出（与 S011 正常行为一致）
  - 控制测试：sort=name DESC → 非法值回退默认列 id，顺序不变（不反转）
  - 仅观察排序结果变化，不使用延时、不读敏感数据
- ground_truth 待 D 运行确认后，经双人复核回填 manifest（保持 null 直至复核通过）。
