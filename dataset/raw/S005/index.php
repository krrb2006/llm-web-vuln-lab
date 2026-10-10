<?php
/**
 * 按关键词模糊搜索页面：读取查询参数，在 lab_people 表中按姓名模糊匹配并展示结果。
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
