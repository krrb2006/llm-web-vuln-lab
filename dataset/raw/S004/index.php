<?php
/**
 * S004 —— 数字 ID 查询（构造目标：修复版；真实标签待验证）
 *
 * 业务：与 S003 相同，读取 GET 参数 id，在 lab_people 表中按数字 ID 精确查询并展示。
 *
 * 修复方式：严格的 ID 输入校验（仅接受十进制数字串）+ 预处理语句参数绑定，
 *           id 仅作为查询值进入，不参与 SQL 语法结构。
 *
 * 输出约定：展示数据库内容时做 HTML 编码，避免引入额外的反射型 XSS。
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
