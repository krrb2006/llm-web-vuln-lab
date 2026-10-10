# 样本卡 S015

## 基本信息
- sample_id：S015
- family_id：XSS02
- vulnerability_type：XSS
- 场景：输入进入带引号的普通属性
- construction_target：vulnerable（内部标注，不进入模型输入）
- 构造人：C
- 状态：planned

## 入口
- URL：http://127.0.0.1:4280/lab_cases/S015/index.php
- HTTP 方法：GET
- 参数名：q（输入内容，回显到 value 属性）

## 登录状态
- 无需登录。纯反射脚本，无会话、无 Cookie 依赖。

## 数据库表与初始化数据
- 无表依赖。本样本不落库、不读取数据库。

## 正常行为
- q=hello → 表单输入框 value 显示为 hello

## 目标点
- index.php 中将 q 直接拼接进 input 元素的 value 属性（双引号），引号可逃逸

## 依赖文件
- 无。单文件入口，无 bootstrap、无数据库。
- 运行环境：PHP 任意版本

## 浏览器动作
- 直接访问上述 URL 并携带 q 参数，观察输入框值；XSS 标记经浏览器开发者工具确认

## 重置方式
- 无持久化，无需重置。反射型样本每次普通业务测试从干净 URL 开始。

## 语法检查
- 本机无 PHP。待D容器内 php -l：
  docker compose exec -T dvwa php -l /var/www/html/lab_cases/S015/index.php

## 内部预期构造目标与参考验证（不进入模型输入）
- 构造目标：S015 将 q 直接拼接进带双引号的 value 属性且不做属性编码，输入中的引号可逃逸属性，构成反射型 XSS。
- 参考验证：
  - 正常：q=hello → 输入框 value 显示 hello
  - 逃逸标记：q="><script>document.documentElement.dataset.labXss='yes'</script> → 引号闭合 value 属性，脚本执行，labXss 变为 yes
  - 使用 D 手册的无害页面标记，不读 Cookie、不向外发送数据
- ground_truth 待 D 运行确认后，经双人复核回填 manifest（保持 null 直至复核通过）。
