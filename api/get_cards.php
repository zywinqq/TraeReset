<?php
/**
 * 卡密列表API（支持分页）
 */
require_once __DIR__ . '/config.php';

header('Content-Type: application/json; charset=utf-8');

$page = isset($_GET['page']) ? intval($_GET['page']) : 1;
$perPage = isset($_GET['per_page']) ? intval($_GET['per_page']) : 15;
if ($page < 1) $page = 1;
if ($perPage < 1 || $perPage > 100) $perPage = 15;
$offset = ($page - 1) * $perPage;

$conn = get_db_connection();
if (!$conn) {
    echo json_encode(['total' => 0, 'page' => 1, 'pages' => 0, 'data' => []]);
    exit;
}

// 总数
$total_result = $conn->query("SELECT COUNT(*) as cnt FROM cards");
$total = $total_result->fetch_assoc()['cnt'];
$pages = ceil($total / $perPage);

// 分页数据
$result = $conn->query("SELECT *, JSON_LENGTH(bound_devices) as bound_devices_count FROM cards ORDER BY id DESC LIMIT $perPage OFFSET $offset");
$cards = [];
while ($row = $result->fetch_assoc()) {
    // 先使用 count 计算状态，然后再 unset
    $boundCount = intval($row['bound_devices_count']);
    $row['bound_devices'] = $boundCount;
    unset($row['bound_devices_count']);
    
    // 动态计算显示状态：按 bound_devices 数量判断
    if ($row['status'] === 'expired') {
        $row['display_status'] = '已过期';
    } elseif ($row['status'] === 'invalid') {
        $row['display_status'] = '已禁用';
    } elseif ($boundCount > 0) {
        $row['display_status'] = '已激活';
    } else {
        $row['display_status'] = '未激活';
    }
    
    // 在线状态：5分钟内活跃（使用UNIX_TIMESTAMP比较，避免PHP时区差异）
    $online_result = $conn->query("SELECT 1 FROM DUAL WHERE UNIX_TIMESTAMP() - UNIX_TIMESTAMP('" . $conn->real_escape_string($row['last_use_time']) . "') <= 300");
    $row['is_online'] = $online_result && $online_result->num_rows > 0 ? 1 : 0;
    
    $cards[] = $row;
}

echo json_encode(['total' => $total, 'page' => $page, 'pages' => $pages, 'per_page' => $perPage, 'data' => $cards], JSON_UNESCAPED_UNICODE);
$conn->close();
exit;
?>
