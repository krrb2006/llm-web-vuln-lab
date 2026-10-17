<?php
declare(strict_types=1);
require __DIR__ . '/../../../../dataset/raw/common/db_connect.php';

$id = (int)($_GET['id'] ?? 0);
$load = $conn->prepare('SELECT nickname FROM profiles WHERE id = ?');
$load->bind_param('i', $id);
$load->execute();
$nickname = (string)($load->get_result()->fetch_assoc()['nickname'] ?? '');

try {
    $result = $conn->query("SELECT id, nickname FROM profiles WHERE nickname = '$nickname'");
    foreach ($result as $row) {
        echo htmlspecialchars((string)$row['nickname'], ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
    }
} catch (Throwable $exception) {
    error_log($exception->getMessage());
}
