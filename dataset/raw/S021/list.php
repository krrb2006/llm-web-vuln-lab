<?php
declare(strict_types=1);

require_once __DIR__ . '/../common/db_connect.php';

$sampleId = basename(__DIR__);
$drafts = [];
try {
    $list = $db->prepare(
        'SELECT id, title FROM lab_preview_drafts WHERE sample_id = ? ORDER BY id DESC LIMIT 20'
    );
    $list->bind_param('s', $sampleId);
    $list->execute();
    $drafts = $list->get_result()->fetch_all(MYSQLI_ASSOC);
    $list->close();
} catch (Throwable $exception) {
    error_log('S021 draft list failed: ' . $exception->getMessage());
}
header('Content-Type: text/html; charset=UTF-8');
?>
<!doctype html>
<html lang="zh-CN">
<head><meta charset="utf-8"><title>草稿列表</title></head>
<body>
<h1>草稿列表</h1>
<p><a href="submit.php">新建草稿</a></p>
<ul>
<?php foreach ($drafts as $draft): ?>
  <li><a href="preview.php?id=<?php echo (int) $draft['id']; ?>"><?php echo htmlspecialchars($draft['title'], ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); ?></a></li>
<?php endforeach; ?>
</ul>
</body>
</html>
