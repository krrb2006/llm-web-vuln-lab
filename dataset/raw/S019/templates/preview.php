<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>内容预览</title>
</head>
<body>
  <h1>内容预览</h1>
  <form method="post" action="index.php">
    <label for="content">内容</label>
    <textarea id="content" name="content" rows="4" cols="50"><?php echo htmlspecialchars($content, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); ?></textarea>
    <button type="submit">预览</button>
  </form>
  <section aria-label="预览结果">
    <h2>预览结果</h2>
    <div class="preview"><?php echo $content; ?></div>
  </section>
</body>
</html>
