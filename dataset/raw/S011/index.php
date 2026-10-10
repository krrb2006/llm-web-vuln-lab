<?php
// 共享 bootstrap.php 提供已连接的 mysqli 连接 $db（host/user/pass/dbname 由 D 配置）。
// 依赖约定详见 sample_card.md；此处不包含数据库口令。
require __DIR__ . '/bootstrap.php';
$db->set_charset('utf8mb4');

// 读取排序字段参数，例如 sort=name；为空时按 id 排序
$sort = trim($_GET['sort'] ?? '');
if ($sort === '') {
    $sort = 'id';
}

$sql = "SELECT id, name FROM lab_people ORDER BY $sort";
$result = $db->query($sql);
if ($result === false) {
    // 查询失败仅写入日志，不向页面回显数据库错误细节
    error_log('lab_people order query failed: ' . $db->error);
    $rows = [];
} else {
    $rows = $result->fetch_all(MYSQLI_ASSOC);
    $result->free();
}
?>
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>教学人员列表</title>
</head>
<body>
<h1>教学人员列表</h1>
<?php if (count($rows) === 0): ?>
<p>未找到匹配记录。</p>
<?php else: ?>
<ul>
<?php foreach ($rows as $row): ?>
<li><?php echo htmlspecialchars((string) $row['id'], ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); ?>：<?php echo htmlspecialchars((string) $row['name'], ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); ?></li>
<?php endforeach; ?>
</ul>
<?php endif; ?>
</body>
</html>
