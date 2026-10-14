<?php
/**
 * 按关键词模糊搜索页面：读取查询参数，在 lab_people 表中按姓名模糊匹配并展示结果。
 */
require_once __DIR__ . '/../common/db_connect.php';

$q = $_GET['q'] ?? '';

try {
    $sql = "SELECT id, name FROM lab_people WHERE name LIKE '%" . $q . "%'";
    $result = $db->query($sql);
    $rows = $result->fetch_all(MYSQLI_ASSOC);
    $result->free();
} catch (Throwable $e) {
    error_log('S005 query failed: ' . $e->getMessage());
    echo '<p>查询失败，请检查输入后重试。</p>';
    exit;
}

echo '<h1>查询结果</h1>';
foreach ($rows as $row) {
    echo '<p>ID ' . htmlspecialchars((string)$row['id'], ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8')
       . '：' . htmlspecialchars($row['name'], ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8') . '</p>';
}
