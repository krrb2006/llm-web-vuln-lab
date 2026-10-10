<?php
/**
 * 按姓名精确查询页面：读取查询参数，在 lab_people 表中查询并展示结果。
 */
require_once __DIR__ . '/../common/db_connect.php';

$name = $_GET['name'] ?? '';

$stmt = $db->prepare('SELECT id, name FROM lab_people WHERE name = ?');
if ($stmt === false) {
    error_log('S002 prepare failed: ' . $db->error);
    echo '<p>查询失败，请检查输入后重试。</p>';
    exit;
}
$stmt->bind_param('s', $name);
$stmt->execute();
$result = $stmt->get_result();

echo '<h1>查询结果</h1>';
while ($row = $result->fetch_assoc()) {
    echo '<p>ID ' . htmlspecialchars((string)$row['id'], ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8')
       . '：' . htmlspecialchars($row['name'], ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8') . '</p>';
}
$stmt->close();
