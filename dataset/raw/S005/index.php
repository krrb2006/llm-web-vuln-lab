<?php
/**
 * S005 —— 按关键词模糊搜索（构造目标：有漏洞；真实标签待验证）
 *
 * 业务：读取 GET 参数 q，在 lab_people 表中按姓名模糊匹配（LIKE）并展示。
 *
 * 目标缺陷：SQL 注入。q 未经参数化，直接拼入 LIKE 查询的字符串字面量中。
 *
 * 说明：LIKE 的通配符（% / _）匹配行为与 SQL 注入是两回事——输入 % 或 _ 可能
 *       改变匹配范围，但不能据此认定 SQL 语法被注入。注入需用真假条件改变结果集来证明。
 *
 * 输出约定：展示数据库内容时做 HTML 编码，避免引入额外的反射型 XSS。
 */
require_once __DIR__ . '/../common/db_connect.php';

$q = $_GET['q'] ?? '';

$sql = "SELECT id, name FROM lab_people WHERE name LIKE '%" . $q . "%'";
$result = $db->query($sql);
if ($result === false) {
    error_log('S005 query failed: ' . $db->error);
    echo '<p>查询失败，请检查输入后重试。</p>';
    exit;
}

echo '<h1>查询结果</h1>';
while ($row = $result->fetch_assoc()) {
    echo '<p>ID ' . htmlspecialchars((string)$row['id'], ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8')
       . '：' . htmlspecialchars($row['name'], ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8') . '</p>';
}
$result->free();
