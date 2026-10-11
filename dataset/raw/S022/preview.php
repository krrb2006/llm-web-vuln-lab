<?php
declare(strict_types=1);

require_once __DIR__ . '/../common/db_connect.php';

$sampleId = basename(__DIR__);
$draftId = filter_input(INPUT_GET, 'id', FILTER_VALIDATE_INT);
if ($draftId === null || $draftId === false || $draftId < 1) {
    http_response_code(400);
    exit('草稿编号无效。');
}

$lookup = $db->prepare(
    'SELECT title, body FROM lab_preview_drafts WHERE sample_id = ? AND id = ?'
);
$lookup->bind_param('si', $sampleId, $draftId);
$lookup->execute();
$draft = $lookup->get_result()->fetch_assoc();
$lookup->close();
if ($draft === null || $draft === false) {
    http_response_code(404);
    exit('草稿不存在。');
}

header('Content-Type: text/html; charset=UTF-8');
?>
<!doctype html>
<html lang="zh-CN">
<head><meta charset="utf-8"><title>草稿预览</title></head>
<body>
<h1><?php echo htmlspecialchars($draft['title'], ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); ?></h1>
<div class="draft-body" style="white-space: pre-wrap"><?php echo htmlspecialchars($draft['body'], ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); ?></div>
<p><a href="list.php">返回草稿列表</a></p>
</body>
</html>
