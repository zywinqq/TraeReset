<?php
require_once __DIR__ . '/config.php';

header('Content-Type: application/json; charset=utf-8');

// 启动 session
session_start();

$action = $_POST['action'] ?? 'login';

if ($action === 'logout') {
    session_destroy();
    echo json_encode(['success' => true, 'message' => '已退出登录']);
    exit;
}

if ($action === 'check') {
    // 检查登录状态
    if (isset($_SESSION['admin_logged_in']) && $_SESSION['admin_logged_in'] === true) {
        echo json_encode(['success' => true]);
    } else {
        echo json_encode(['success' => false]);
    }
    exit;
}

// 登录
$password = $_POST['password'] ?? '';
if (empty($password)) {
    echo json_encode(['success' => false, 'message' => '密码不能为空']);
    exit;
}

$input_md5 = md5(trim($password));

if ($input_md5 === ADMIN_PASSWORD_MD5) {
    $_SESSION['admin_logged_in'] = true;
    $_SESSION['login_time'] = time();
    echo json_encode(['success' => true, 'message' => '登录成功']);
} else {
    echo json_encode(['success' => false, 'message' => '密码错误，请重试']);
}
exit;
?>
