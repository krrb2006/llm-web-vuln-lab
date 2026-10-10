<?php
/**
 * 入口：接收按姓名查询参数，调用数据访问层查询 lab_people 表并展示结果。
 */
require_once __DIR__ . '/../common/db_connect.php';
require_once __DIR__ . '/repository.php';

$name = $_GET['name'] ?? '';

$result = find_people_by_name($db, $name);
if ($result === false) {
    error_log('name query failed: ' . $db->error);
    echo '<p>查询失败，请检查输入后重试。</p>';
    exit;
}

echo '<h1>查询结果</h1>';
while ($row = $result->fetch_assoc()) {
    echo '<p>ID ' . htmlspecialchars((string)$row['id'], ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8')
       . '：' . htmlspecialchars($row['name'], ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8') . '</p>';
}
$result->free();
