<?php
/**
 * 心跳检测API - 客户端每5分钟调用一次
 */
require_once __DIR__ . '/config.php';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    api_response(false, '请求方法错误');
}

$card_key = trim($_POST['card_key'] ?? '');
$machine_id = trim($_POST['machine_id'] ?? '');

if (empty($card_key) || empty($machine_id)) {
    api_response(false, '参数不完整');
}

$conn = get_db_connection();
if (!$conn) {
    api_response(false, '服务器错误');
}

$stmt = $conn->prepare("SELECT * FROM cards WHERE card_key = ?");
$stmt->bind_param('s', $card_key);
$stmt->execute();
$result = $stmt->get_result();

if ($result->num_rows == 0) {
    $stmt->close(); $conn->close();
    api_response(false, '卡密不存在', ['action' => 'exit']);
}

$card = $result->fetch_assoc();
$stmt->close();

// 检查是否过期
if (!empty($card['expire_date']) && $card['expire_date'] < date('Y-m-d')) {
    $conn->close();
    api_response(false, '卡密已过期', ['action' => 'exit']);
}

// 检查状态
if ($card['status'] === 'invalid') {
    $conn->close();
    api_response(false, '卡密已被禁用', ['action' => 'exit']);
}

// 检查此设备是否在绑定列表中
$bound_devices = [];
if (!empty($card['bound_devices'])) {
    $bound_devices = json_decode($card['bound_devices'], true);
    if (!is_array($bound_devices)) $bound_devices = [];
}

if (!in_array($machine_id, $bound_devices)) {
    $conn->close();
    api_response(false, '此设备未授权', ['action' => 'exit']);
}

// 仅更新心跳时间，不改变卡密状态
$conn->query("UPDATE cards SET last_use_time = NOW() WHERE card_key = '" . $conn->real_escape_string($card_key) . "'");
log_action('HEARTBEAT', $card_key, $machine_id);

$conn->close();
api_response(true, '在线', ['action' => 'continue']);
?>
