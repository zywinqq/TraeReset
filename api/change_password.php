<?php
require_once __DIR__ . '/config.php';

header('Content-Type: application/json; charset=utf-8');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    echo json_encode(['success' => false, 'message' => '请求方法错误']);
    exit;
}

$newPassword = $_POST['new_password'] ?? '';
if (empty($newPassword)) {
    echo json_encode(['success' => false, 'message' => '密码不能为空']);
    exit;
}

// 直接更新 config.php 中的密码常量（需要手动修改）
// 这里使用 MD5 方式更新
$md5pwd = md5(trim($newPassword));

// 输出新的 MD5 值供用户手动更新
echo json_encode([
    'success' => true, 
    'message' => '密码修改成功，请手动更新 config.php 中的 ADMIN_PASSWORD 和 ADMIN_PASSWORD_MD5',
    'new_md5' => $md5pwd
]);
exit;
?>
