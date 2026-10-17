<?php
declare(strict_types=1);

require_once __DIR__ . '/../common/db_connect.php';

$sampleId = basename(__DIR__);
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $title = trim((string) ($_POST['title'] ?? ''));
    $body = (string) ($_POST['body'] ?? '');
    if ($title === '' || strlen($title) > 120 || trim($body) === '' || strlen($body) > 2000) {
        http_response_code(400);
        exit('标题或正文为空，或内容超过长度限制。');
    }

    try {
        $insert = $db->prepare(
            'INSERT INTO lab_preview_drafts (sample_id, title, body) VALUES (?, ?, ?)'
        );
        $insert->bind_param('sss', $sampleId, $title, $body);
        $insert->execute();
        $draftId = $db->insert_id;
        $insert->close();
    } catch (Throwable $exception) {
        error_log('S022 draft insert failed: ' . $exception->getMessage());
        http_response_code(500);
        exit('草稿暂时无法保存，请稍后重试。');
    }
    header('Location: preview.php?id=' . $draftId, true, 303);
    exit;
}

header('Content-Type: text/html; charset=UTF-8');
?>
<!doctype html>
<html lang="zh-CN">
<head><meta charset="utf-8"><title>草稿提交</title></head>
<body>
<h1>提交草稿</h1>
<form method="post" action="submit.php">
  <label for="title">标题</label>
  <input id="title" name="title" type="text" maxlength="120" required>
  <label for="body">正文</label>
  <textarea id="body" name="body" rows="5" cols="50" required></textarea>
  <button type="submit">保存并预览</button>
</form>
<p><a href="list.php">查看草稿列表</a></p>
</body>
</html>
