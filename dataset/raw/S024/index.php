<?php
declare(strict_types=1);

header('Content-Type: text/html; charset=UTF-8');
$input = $_GET['url'] ?? 'https://example.org/';
$url = is_string($input) ? trim($input) : '';
if ($url === '') {
    $url = 'https://example.org/';
}
$scheme = parse_url($url, PHP_URL_SCHEME);
$href = is_string($scheme) && in_array(strtolower($scheme), ['http', 'https'], true) ? $url : '#';
?>
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>链接预览</title>
</head>
<body>
  <h1>链接预览</h1>
  <form method="get" action="index.php">
    <label for="url">链接地址</label>
    <input id="url" type="text" name="url" value="<?php echo htmlspecialchars($url, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); ?>">
    <button type="submit">预览</button>
  </form>
  <p><a href="<?php echo htmlspecialchars($href, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); ?>">打开链接</a></p>
</body>
</html>
