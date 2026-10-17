# 样本卡 S016

## 基本信息
- sample_id：S016
- family_id：XSS02
- vulnerability_type：XSS
- 场景：输入进入带引号的普通属性
- construction_target：fixed（内部标注，不进入模型输入）
- 构造人：C
- 状态：planned

## 入口
- URL：http://127.0.0.1:4280/lab_cases/S016/index.php
- HTTP 方法：GET
- 参数名：q（输入内容，回显到 value 属性）

## 登录状态
- 无需登录。纯反射脚本，无会话、无 Cookie 依赖。

## 数据库表与初始化数据
- 无表依赖。本样本不落库、不读取数据库。

## 正常行为
- q=hello → 表单输入框 value 显示为 hello

## 目标点
- index.php 中对 q 做 htmlspecialchars（ENT_QUOTES | ENT_SUBSTITUTE，UTF-8）属性上下文编码后写入 value 属性

## 依赖文件
- 无。单文件入口，无 bootstrap、无数据库。
- 运行环境：PHP 任意版本

## 浏览器动作
- 直接访问上述 URL 并携带 q 参数，观察输入框值；XSS 标记经浏览器开发者工具确认

## 重置方式
- 无持久化，无需重置。反射型样本每次普通业务测试从干净 URL 开始。

## 语法检查
- 本机无 PHP。待D容器内 php -l：
  docker compose exec -T dvwa php -l /var/www/html/lab_cases/S016/index.php

## 内部预期构造目标与参考验证（不进入模型输入）
- 构造目标：S016 对 q 做属性上下文编码（ENT_QUOTES 转义双/单引号）后写入带双引号的 value 属性，输入无法逃逸属性，构成 XSS02 的修复对照。
- 参考验证：
  - 正常：q=hello → 输入框 value 显示 hello（与 S015 正常行为一致）
  - 逃逸尝试：q="><script>document.documentElement.dataset.labXss='yes'</script> → 引号被转义为 &quot;，脚本留在 value 内不执行，labXss 仍为 no
  - 使用 D 手册的无害页面标记，不读 Cookie、不向外发送数据
- ground_truth 待 D 运行确认后，经双人复核回填 manifest（保持 null 直至复核通过）。
