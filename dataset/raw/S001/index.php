<?php
/**
 * S001 —— 姓名精确查询（构造目标：有漏洞；真实标签待验证）
 *
 * 业务：读取 GET 参数 name，在 lab_people 表中按姓名精确查询并展示。
 *
 * 目标缺陷：SQL 注入。name 未经参数化直接拼入 SQL 语句。
 *
 * 输出约定：展示数据库内容时做 HTML 编码，避免引入额外的反射型 XSS，
 *           以免干扰本样本对 SQL 注入的判定。
 */
require_once __DIR__ . '/../common/db_connect.php';

$name = $_GET['name'] ?? '';

$sql = "SELECT id, name FROM lab_people WHERE name = '" . $name . "'";
$result = $db->query($sql);
if ($result === false) {
    error_log('S001 query failed: ' . $db->error);
    echo '<p>查询失败，请检查输入后重试。</p>';
    exit;
}

echo '<h1>查询结果</h1>';
while ($row = $result->fetch_assoc()) {
    echo '<p>ID ' . htmlspecialchars((string)$row['id'], ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8')
       . '：' . htmlspecialchars($row['name'], ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8') . '</p>';
}
$result->free();
