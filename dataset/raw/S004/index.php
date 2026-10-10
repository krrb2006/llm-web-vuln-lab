<?php
/**
 * 按数字 ID 查询页面：读取查询参数，在 lab_people 表中查询并展示结果。
 */
require_once __DIR__ . '/../common/db_connect.php';

$id_raw = $_GET['id'] ?? '';

if ($id_raw === '' || !ctype_digit($id_raw)) {
    error_log('S004 rejected non-numeric id: ' . $id_raw);
    echo '<p>非法的 ID 参数。</p>';
    exit;
}
$id = (int)$id_raw;

$stmt = $db->prepare('SELECT id, name FROM lab_people WHERE id = ?');
if ($stmt === false) {
    error_log('S004 prepare failed: ' . $db->error);
    echo '<p>查询失败，请检查输入后重试。</p>';
    exit;
}
$stmt->bind_param('i', $id);
$stmt->execute();
$result = $stmt->get_result();

echo '<h1>查询结果</h1>';
while ($row = $result->fetch_assoc()) {
    echo '<p>ID ' . htmlspecialchars((string)$row['id'], ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8')
       . '：' . htmlspecialchars($row['name'], ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8') . '</p>';
}
$stmt->close();
