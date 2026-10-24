<?php
declare(strict_types=1);

require_once __DIR__ . '/../common/db_connect.php';

$sampleId = basename(__DIR__);
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $body = (string) ($_POST['body'] ?? '');
    if (trim($body) === '' || strlen($body) > 2000) {
        http_response_code(400);
        exit('留言不能为空且不能超过 2000 字节。');
    }

    try {
        $insert = $db->prepare('INSERT INTO lab_guestbook (sample_id, body) VALUES (?, ?)');
        $insert->bind_param('ss', $sampleId, $body);
        $insert->execute();
        $insert->close();
    } catch (Throwable $exception) {
        error_log('S018 guestbook insert failed: ' . $exception->getMessage());
        http_response_code(500);
        exit('留言暂时无法保存，请稍后重试。');
    }
    header('Location: index.php', true, 303);
    exit;
}

$messages = [];
try {
    $list = $db->prepare('SELECT body FROM lab_guestbook WHERE sample_id = ? ORDER BY id DESC LIMIT 20');
    $list->bind_param('s', $sampleId);
    $list->execute();
    $messages = $list->get_result()->fetch_all(MYSQLI_ASSOC);
    $list->close();
} catch (Throwable $exception) {
    error_log('S018 guestbook list failed: ' . $exception->getMessage());
}
header('Content-Type: text/html; charset=UTF-8');
?>
<!doctype html>
<html lang="zh-CN">
<head><meta charset="utf-8"><title>访客留言板</title></head>
<body>
<h1>访客留言板</h1>
<form method="post" action="index.php">
  <label for="body">留言</label>
  <textarea id="body" name="body" rows="3" cols="50" required></textarea>
  <button type="submit">发布</button>
</form>
<h2>最近留言</h2>
<ul>
<?php foreach ($messages as $message): ?>
  <li><div style="white-space: pre-wrap"><?php echo htmlspecialchars($message['body'], ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); ?></div></li>
<?php endforeach; ?>
</ul>
</body>
</html>
