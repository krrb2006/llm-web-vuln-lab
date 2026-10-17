<?php
declare(strict_types=1);
require __DIR__ . '/../../../../dataset/raw/common/db_connect.php';

$nickname = (string)($_POST['nickname'] ?? '');
$stmt = $conn->prepare('INSERT INTO profiles (nickname) VALUES (?)');
$stmt->bind_param('s', $nickname);
$stmt->execute();

echo 'saved';
