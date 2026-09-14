<?php
require_once __DIR__ . '/config.php';

header('Content-Type: application/json; charset=utf-8');

$key = $_GET['key'] ?? '';
$status = $_GET['status'] ?? '';

$conn = get_db_connection();
if (!$conn) {
    echo json_encode([]);
    exit;
}

$sql = "SELECT *, JSON_LENGTH(bound_devices) as bound_devices_count FROM cards WHERE 1=1";
$params = [];
$types = '';

if (!empty($key)) {
    $sql .= " AND card_key LIKE ?";
    $params[] = "%$key%";
    $types .= 's';
}
if (!empty($status)) {
    $sql .= " AND status = ?";
    $params[] = $status;
    $types .= 's';
}

$sql .= " ORDER BY id DESC";

$stmt = $conn->prepare($sql);
if (!empty($params)) {
    $stmt->bind_param($types, ...$params);
}
$stmt->execute();
$result = $stmt->get_result();

$cards = [];
while ($row = $result->fetch_assoc()) {
    // 先使用 count 计算状态
    $boundCount = intval($row['bound_devices_count']);
    $row['bound_devices'] = $boundCount;
    unset($row['bound_devices_count']);
    
    // 动态计算显示状态
    if ($row['status'] === 'expired') {
        $row['display_status'] = '已过期';
    } elseif ($row['status'] === 'invalid') {
        $row['display_status'] = '已禁用';
    } elseif ($boundCount > 0) {
        $row['display_status'] = '已激活';
    } else {
        $row['display_status'] = '未激活';
    }
    
    // 在线状态：使用UNIX_TIMESTAMP比较，避免PHP时区差异
    $row['is_online'] = 0;
    if (!empty($row['last_use_time'])) {
        $online_check = $conn->query("SELECT 1 FROM DUAL WHERE UNIX_TIMESTAMP() - UNIX_TIMESTAMP('" . $conn->real_escape_string($row['last_use_time']) . "') <= 300");
        if ($online_check && $online_check->num_rows > 0) {
            $row['is_online'] = 1;
        }
    }
    
    $cards[] = $row;
}

$stmt->close();
$conn->close();

echo json_encode($cards, JSON_UNESCAPED_UNICODE);
exit;
?>
