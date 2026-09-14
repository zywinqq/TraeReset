<?php
require_once __DIR__ . '/config.php';

header('Content-Type: application/json; charset=utf-8');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    echo json_encode(['success' => false, 'message' => '请求方法错误'], JSON_UNESCAPED_UNICODE);
    exit;
}

$cardKey = $_POST['card_key'] ?? '';
if (empty($cardKey)) {
    echo json_encode(['success' => false, 'message' => '卡密不能为空'], JSON_UNESCAPED_UNICODE);
    exit;
}

$conn = get_db_connection();
if (!$conn) {
    echo json_encode(['success' => false, 'message' => '数据库连接失败'], JSON_UNESCAPED_UNICODE);
    exit;
}

// 检查卡密是否存在
$check = $conn->prepare("SELECT id FROM cards WHERE card_key = ?");
$check->bind_param('s', $cardKey);
$check->execute();
$result = $check->get_result();

if ($result->num_rows === 0) {
    $check->close();
    $conn->close();
    echo json_encode(['success' => false, 'message' => '卡密不存在'], JSON_UNESCAPED_UNICODE);
    exit;
}
$check->close();

// 可更新的字段
$updates = [];
$types = '';
$values = [];

// 卡密类型
if (isset($_POST['card_type']) && $_POST['card_type'] !== '') {
    $cardType = $_POST['card_type'];
    $updates[] = 'card_type = ?';
    $types .= 's';
    $values[] = $cardType;
}

// 过期日期 (null表示永久)
if (isset($_POST['expire_date'])) {
    $expireDate = $_POST['expire_date'];
    if ($expireDate === '' || $expireDate === 'null') {
        $updates[] = 'expire_date = NULL';
    } else {
        $updates[] = 'expire_date = ?';
        $types .= 's';
        $values[] = $expireDate;
    }
}

// 最大使用次数 (-1表示不限制)
if (isset($_POST['max_uses'])) {
    $maxUses = intval($_POST['max_uses']);
    $updates[] = 'max_uses = ?';
    $types .= 'i';
    $values[] = $maxUses;
}

// 最大设备数
if (isset($_POST['max_devices'])) {
    $maxDevices = intval($_POST['max_devices']);
    if ($maxDevices < 1) $maxDevices = 1;
    $updates[] = 'max_devices = ?';
    $types .= 'i';
    $values[] = $maxDevices;
}

// 卡密状态
if (isset($_POST['status']) && $_POST['status'] !== '') {
    $status = $_POST['status'];
    if (in_array($status, ['active', 'expired', 'invalid', 'used'])) {
        $updates[] = 'status = ?';
        $types .= 's';
        $values[] = $status;
    }
}

if (empty($updates)) {
    $conn->close();
    echo json_encode(['success' => false, 'message' => '没有要更新的字段'], JSON_UNESCAPED_UNICODE);
    exit;
}

// 构建更新语句
$sql = "UPDATE cards SET " . implode(', ', $updates) . " WHERE card_key = ?";
$types .= 's';
$values[] = $cardKey;

$stmt = $conn->prepare($sql);
if (!$stmt) {
    $conn->close();
    echo json_encode(['success' => false, 'message' => 'SQL准备失败: ' . $conn->error], JSON_UNESCAPED_UNICODE);
    exit;
}

// 动态绑定参数
$params = [];
$params[] = $types;
foreach ($values as $v) {
    $params[] = $v;
}
$stmt->bind_param(...$params);

if ($stmt->execute()) {
    log_action('EDIT_CARD', $cardKey);
    echo json_encode([
        'success' => true, 
        'message' => '卡密属性更新成功',
        'card_key' => $cardKey
    ], JSON_UNESCAPED_UNICODE);
} else {
    echo json_encode(['success' => false, 'message' => '更新失败: ' . $stmt->error], JSON_UNESCAPED_UNICODE);
}

$stmt->close();
$conn->close();
exit;
?>
