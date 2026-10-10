<?php
/**
 * S002 —— 姓名精确查询（构造目标：修复版；真实标签待验证）
 *
 * 业务：与 S001 相同，读取 GET 参数 name，在 lab_people 表中按姓名精确查询并展示。
 *
 * 修复方式：预处理语句 + 参数绑定，name 仅作为查询值进入，不参与 SQL 语法结构。
 *
 * 输出约定：展示数据库内容时做 HTML 编码，避免引入额外的反射型 XSS。
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
