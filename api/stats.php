<?php
/**
 * 统计数据API
 */
require_once __DIR__ . '/config.php';

header('Content-Type: application/json; charset=utf-8');

$conn = get_db_connection();
if (!$conn) {
    echo json_encode(['total' => 0, 'activated' => 0, 'used' => 0, 'expired' => 0, 'inactive' => 0, 'online' => 0]);
    exit;
}

// 已激活=已绑定设备, 未激活=未绑定且有效, 已使用=有使用记录
$result = $conn->query("SELECT 
    COUNT(*) as total,
    SUM(CASE WHEN JSON_LENGTH(bound_devices) > 0 THEN 1 ELSE 0 END) as activated,
    SUM(CASE WHEN JSON_LENGTH(bound_devices) = 0 AND status != 'expired' AND status != 'invalid' THEN 1 ELSE 0 END) as inactive,
    SUM(CASE WHEN last_use_time IS NOT NULL THEN 1 ELSE 0 END) as used,
    SUM(CASE WHEN status = 'expired' THEN 1 ELSE 0 END) as expired
FROM cards");
$row = $result->fetch_assoc();

// 在线设备数：5分钟内有使用记录的卡密（纯SQL比较，避免PHP时区问题）
$online_result = $conn->query("SELECT COUNT(*) as online FROM cards WHERE last_use_time IS NOT NULL AND UNIX_TIMESTAMP() - UNIX_TIMESTAMP(last_use_time) <= 300");
$online_row = $online_result->fetch_assoc();
$row['online'] = intval($online_row['online'] ?? 0);

echo json_encode($row, JSON_UNESCAPED_UNICODE);
$conn->close();
exit;
?>
