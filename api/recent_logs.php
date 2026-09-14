<?php
require_once __DIR__ . '/config.php';

header('Content-Type: application/json; charset=utf-8');

$conn = get_db_connection();
if (!$conn) {
    echo json_encode([]);
    exit;
}

$result = $conn->query("SELECT card_key, card_type, bound_devices, last_use_time, use_count
    FROM cards WHERE last_use_time IS NOT NULL AND JSON_LENGTH(bound_devices) > 0
    ORDER BY last_use_time DESC LIMIT 10");

$logs = [];
$now = time();
while ($row = $result->fetch_assoc()) {
    $devices = json_decode($row['bound_devices'], true);
    $last_device = is_array($devices) && count($devices) > 0 ? end($devices) : '';
    
    // 在线状态：5分钟内活跃（使用UNIX_TIMESTAMP比较，避免PHP时区差异）
    if (!empty($row['last_use_time'])) {
        $online_check = $conn->query("SELECT 1 FROM DUAL WHERE UNIX_TIMESTAMP() - UNIX_TIMESTAMP('" . $conn->real_escape_string($row['last_use_time']) . "') <= 300");
        $is_online = ($online_check && $online_check->num_rows > 0) ? 1 : 0;
    } else {
        $is_online = 0;
    }
    
    $logs[] = [
        'card_key' => $row['card_key'],
        'card_type' => $row['card_type'],
        'machine_id' => $last_device,
        'use_count' => $row['use_count'],
        'last_use_time' => $row['last_use_time'],
        'is_online' => $is_online
    ];
}

$conn->close();
echo json_encode($logs, JSON_UNESCAPED_UNICODE);
exit;
?>
