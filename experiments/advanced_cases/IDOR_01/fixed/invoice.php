<?php
declare(strict_types=1);
session_start();
require __DIR__ . '/../../../../dataset/raw/common/db_connect.php';

$invoiceId = (int)($_GET['id'] ?? 0);
$currentUserId = (int)($_SESSION['user_id'] ?? 0);
$stmt = $conn->prepare(
    'SELECT id, owner_id, total FROM invoices WHERE id = ? AND owner_id = ?'
);
$stmt->bind_param('ii', $invoiceId, $currentUserId);
$stmt->execute();
$invoice = $stmt->get_result()->fetch_assoc();

if ($invoice !== null) {
    echo json_encode($invoice, JSON_UNESCAPED_UNICODE | JSON_THROW_ON_ERROR);
}
