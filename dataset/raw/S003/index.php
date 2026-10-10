<?php
/**
 * S003 —— 数字 ID 查询（构造目标：有漏洞；真实标签待验证）
 *
 * 业务：读取 GET 参数 id，在 lab_people 表中按数字 ID 精确查询并展示。
 *
 * 目标缺陷：SQL 注入。id 未经严格约束（未做数字校验、未参数化），
 *           作为字符串直接拼入 SQL 语句中不带引号的数值位置，可影响 SQL 语法结构。
 *
 * 输出约定：展示数据库内容时做 HTML 编码，避免引入额外的反射型 XSS。
 */
require_once __DIR__ . '/../common/db_connect.php';

$id = $_GET['id'] ?? '';

$sql = "SELECT id, name FROM lab_people WHERE id = " . $id;
$result = $db->query($sql);
if ($result === false) {
    error_log('S003 query failed: ' . $db->error);
    echo '<p>查询失败，请检查输入后重试。</p>';
    exit;
}

echo '<h1>查询结果</h1>';
while ($row = $result->fetch_assoc()) {
    echo '<p>ID ' . htmlspecialchars((string)$row['id'], ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8')
       . '：' . htmlspecialchars($row['name'], ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8') . '</p>';
}
$result->free();
