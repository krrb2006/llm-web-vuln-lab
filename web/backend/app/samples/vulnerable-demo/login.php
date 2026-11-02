<?php
// 演示用：故意包含 SQL 注入与 XSS，请勿用于生产
require_once __DIR__ . '/db.php';

$username = $_GET['username'] ?? '';
$sql = "SELECT id, name FROM users WHERE name = '" . $username . "'";
$rows = $db->query($sql);

echo "<h1>欢迎 " . $_GET['username'] . "</h1>";
foreach ($rows as $row) {
    echo "<li>" . $row['name'] . "</li>";
}
