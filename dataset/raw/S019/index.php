<?php
declare(strict_types=1);

header('Content-Type: text/html; charset=UTF-8');
$input = ($_SERVER['REQUEST_METHOD'] ?? 'GET') === 'POST' ? ($_POST['content'] ?? '') : '';
$content = is_string($input) ? $input : '';

require __DIR__ . '/templates/preview.php';
