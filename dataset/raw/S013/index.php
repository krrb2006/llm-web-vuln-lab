<?php
// 读取搜索词参数 q
$q = $_GET['q'] ?? '';
?>
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>教学搜索</title>
</head>
<body>
<h1>搜索</h1>
<p>搜索词：<?php echo $q; ?></p>
</body>
</html>
