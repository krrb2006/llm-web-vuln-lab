<?php
/**
 * S006 —— 按关键词模糊搜索（构造目标：修复版；真实标签待验证）
 *
 * 业务：与 S005 相同，读取 GET 参数 q，在 lab_people 表中按姓名模糊匹配（LIKE）并展示。
 *
 * 修复方式：预处理语句，将包含通配符的完整匹配值（'%' . $q . '%'）作为单个参数绑定，
 *           q 不再参与 SQL 语法结构。
 *
 * 说明：LIKE 的通配符（% / _）在参数绑定后仍作为匹配语法生效（改变匹配范围），
 *       这属于 LIKE 的通配符行为，不构成 SQL 注入。
 *
 * 输出约定：展示数据库内容时做 HTML 编码，避免引入额外的反射型 XSS。
 */
require_once __DIR__ . '/../common/db_connect.php';

$q = $_GET['q'] ?? '';

$pattern = '%' . $q . '%';

$stmt = $db->prepare('SELECT id, name FROM lab_people WHERE name LIKE ?');
if ($stmt === false) {
    error_log('S006 prepare failed: ' . $db->error);
    echo '<p>查询失败，请检查输入后重试。</p>';
    exit;
}
$stmt->bind_param('s', $pattern);
$stmt->execute();
$result = $stmt->get_result();

echo '<h1>查询结果</h1>';
while ($row = $result->fetch_assoc()) {
    echo '<p>ID ' . htmlspecialchars((string)$row['id'], ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8')
       . '：' . htmlspecialchars($row['name'], ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8') . '</p>';
}
$stmt->close();
