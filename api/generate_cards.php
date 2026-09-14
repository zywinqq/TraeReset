<?php
require_once __DIR__ . '/config.php';

header('Content-Type: application/json; charset=utf-8');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    echo json_encode(['success' => false, 'message' => '请求方法错误'], JSON_UNESCAPED_UNICODE);
    exit;
}

$count = intval($_POST['count'] ?? 10);
$type = $_POST['type'] ?? 'normal';
$days = intval($_POST['days'] ?? 365);
$maxUses = intval($_POST['maxUses'] ?? -1);
$maxDevices = intval($_POST['maxDevices'] ?? 1);

if ($count < 1 || $count > 1000) {
    echo json_encode(['success' => false, 'message' => '生成数量必须在1-1000之间'], JSON_UNESCAPED_UNICODE);
    exit;
}

$conn = get_db_connection();
if (!$conn) {
    echo json_encode(['success' => false, 'message' => '数据库连接失败'], JSON_UNESCAPED_UNICODE);
    exit;
}

$cards = [];
$stmt = $conn->prepare("INSERT INTO cards (card_key, card_type, expire_date, max_uses, max_devices) VALUES (?, ?, ?, ?, ?)");
if (!$stmt) {
    $errorMsg = $conn->error;
    $conn->close();
    echo json_encode(['success' => false, 'message' => "SQL错误: " . $errorMsg], JSON_UNESCAPED_UNICODE);
    exit;
}

for ($i = 0; $i < $count; $i++) {
    // 增强随机性：使用随机字符串+随机数字
    $randStr = substr(str_shuffle('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'), 0, 6);
    $randNum = str_pad(mt_rand(0, 999999), 6, '0', STR_PAD_LEFT);
    $cardKey = 'TRAE-' . $randStr . '-' . $randNum;
    
    // 确保唯一性
    $check = $conn->query("SELECT id FROM cards WHERE card_key = '$cardKey'");
    if ($check && $check->num_rows > 0) {
        $i--;
        continue;
    }
    
    $expireDate = null;
    if ($days > 0) {
        $expireDate = date('Y-m-d', strtotime("+$days days"));
    }
    
    $stmt->bind_param('sssii', $cardKey, $type, $expireDate, $maxUses, $maxDevices);
    
    if ($stmt->execute()) {
        $cards[] = $cardKey;
    }
}

$stmt->close();
$conn->close();

echo json_encode(['success' => true, 'cards' => $cards], JSON_UNESCAPED_UNICODE);
exit;
?>
