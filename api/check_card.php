<?php
/**
 * 卡密验证API
 */
require_once __DIR__ . '/config.php';
header('Access-Control-Allow-Origin: *');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    api_response(false, '请求方法错误');
}

$card_key = trim($_POST['card_key'] ?? '');
$machine_id = trim($_POST['machine_id'] ?? '');

if (empty($card_key)) {
    api_response(false, '请输入卡密');
}

$conn = get_db_connection();
if (!$conn) {
    api_response(false, '服务器错误');
}

$stmt = $conn->prepare("SELECT * FROM cards WHERE card_key = ? AND status = 'active'");
$stmt->bind_param('s', $card_key);
$stmt->execute();
$result = $stmt->get_result();

if ($result->num_rows == 0) {
    $stmt->close();
    log_action('INVALID_CARD', $card_key, $machine_id);
    $conn->close();
    api_response(false, '卡密不存在或已失效');
}

$card = $result->fetch_assoc();
$stmt->close();

// 检查有效期
if (!empty($card['expire_date']) && $card['expire_date'] < date('Y-m-d')) {
    log_action('EXPIRED', $card_key, $machine_id);
    $conn->close();
    api_response(false, '卡密已过期');
}

// 设备绑定验证
$bound_devices = [];
if (!empty($card['bound_devices'])) {
    $bound_devices = json_decode($card['bound_devices'], true);
    if (!is_array($bound_devices)) $bound_devices = [];
}

$max_devices = $card['max_devices'];

// 检查是否已绑定此设备
if (!empty($machine_id) && in_array($machine_id, $bound_devices)) {
    // 仅更新最后使用时间，不改变状态
    $conn->query("UPDATE cards SET last_use_time = NOW() WHERE card_key = '" . $conn->real_escape_string($card_key) . "'");
    log_action('VALID_CARD', $card_key, $machine_id);
    $conn->close();
    api_response(true, '验证成功', [
        'expire_date' => $card['expire_date'] ?: '永久',
        'card_type' => $card['card_type'],
        'bound_devices' => count($bound_devices),
        'max_devices' => $max_devices
    ]);
}

// 检查设备数是否超限
if ($max_devices > 0 && count($bound_devices) >= $max_devices) {
    log_action('DEVICE_LIMIT', $card_key, $machine_id);
    $conn->close();
    api_response(false, "设备数已达上限($max_devices台)，无法再绑定新设备");
}

// 绑定新设备
if (!empty($machine_id)) {
    $bound_devices[] = $machine_id;
    $bound_json = json_encode($bound_devices);
    $update_stmt = $conn->prepare("UPDATE cards SET bound_devices = ?, last_use_time = NOW(), use_count = use_count + 1 WHERE card_key = ?");
    $update_stmt->bind_param('ss', $bound_json, $card_key);
    $update_stmt->execute();
    $update_stmt->close();
}

log_action('VALID_CARD', $card_key, $machine_id);
$conn->close();

api_response(true, '验证成功', [
    'expire_date' => $card['expire_date'] ?: '永久',
    'card_type' => $card['card_type'],
    'bound_devices' => count($bound_devices),
    'max_devices' => $max_devices
]);
?>
