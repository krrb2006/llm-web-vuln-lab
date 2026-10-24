<?php
// 读取输入参数 q，回显到表单 input 的 value 属性内
$q = $_GET['q'] ?? '';
?>
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>教学表单</title>
</head>
<body>
<h1>留言输入</h1>
<form method="get">
<label>内容：</label>
<input type="text" name="q" value="<?php echo $q; ?>">
<input type="submit" value="提交">
</form>
</body>
</html>
