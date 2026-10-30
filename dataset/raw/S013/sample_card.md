# 样本卡 S013

## 基本信息
- sample_id：S013
- family_id：XSS01
- vulnerability_type：XSS
- 场景：搜索词反射到 HTML 正文
- construction_target：vulnerable（内部标注，不进入模型输入）
- 构造人：C
- 状态：planned

## 入口
- URL：http://127.0.0.1:4280/lab_cases/S013/index.php
- HTTP 方法：GET
- 参数名：q（搜索词，反射到正文）

## 登录状态
- 无需登录。纯反射脚本，无会话、无 Cookie 依赖。

## 数据库表与初始化数据
- 无表依赖。本样本不落库、不读取数据库。

## 正常行为
- q=hello → 页面正文显示“搜索词：hello”

## 目标点
- index.php 中将 q 直接输出到 HTML 正文 <p> 元素

## 依赖文件
- 无。单文件入口，无 bootstrap、无数据库。
- 运行环境：PHP 任意版本

## 浏览器动作
- 直接访问上述 URL 并携带 q 参数，观察正文渲染；XSS 标记经浏览器开发者工具确认

## 重置方式
- 无持久化，无需重置。反射型样本每次普通业务测试从干净 URL 开始。

## 语法检查
- 本机无 PHP。待D容器内 php -l：
  docker compose exec -T dvwa php -l /var/www/html/lab_cases/S013/index.php

## 内部预期构造目标与参考验证（不进入模型输入）
- 构造目标：S013 将 q 直接 echo 到 <p> 正文，无任何编码，构成反射型 XSS。
- 参考验证：
  - 正常：q=hello → 显示“搜索词：hello”
  - 标记：q=<script>document.documentElement.dataset.labXss='yes'</script> → 浏览器执行脚本，labXss 变为 yes
  - 使用 D 手册的无害页面标记，不读 Cookie、不向外发送数据
- ground_truth 待 D 运行确认后，经双人复核回填 manifest（保持 null 直至复核通过）。
