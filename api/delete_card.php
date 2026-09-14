<?php
require_once __DIR__ . '/config.php';

header('Content-Type: application/json; charset=utf-8');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    echo json_encode(['success' => false, 'message' => '请求方法错误']);
    exit;
}

// 支持两种模式：单张删除(card_key) 和 批量删除(card_keys JSON数组)
$cardKey = $_POST['card_key'] ?? '';
$cardKeysJson = $_POST['card_keys'] ?? '';

$conn = get_db_connection();
if (!$conn) {
    echo json_encode(['success' => false, 'message' => '数据库连接失败']);
    exit;
}

// 批量删除
if (!empty($cardKeysJson)) {
    $cardKeys = json_decode($cardKeysJson, true);
    if (!is_array($cardKeys) || empty($cardKeys)) {
        echo json_encode(['success' => false, 'message' => '卡密列表为空']);
        exit;
    }
    
    $placeholders = implode(',', array_fill(0, count($cardKeys), '?'));
    $stmt = $conn->prepare("DELETE FROM cards WHERE card_key IN ($placeholders)");
    
    // 动态绑定参数
    $types = str_repeat('s', count($cardKeys));
    $stmt->bind_param($types, ...$cardKeys);
    
    if ($stmt->execute()) {
        echo json_encode(['success' => true, 'message' => '批量删除成功: ' . $stmt->affected_rows . '张']);
    } else {
        echo json_encode(['success' => false, 'message' => '批量删除失败']);
    }
    $stmt->close();
}
// 单张删除
elseif (!empty($cardKey)) {
    $stmt = $conn->prepare("DELETE FROM cards WHERE card_key = ?");
    $stmt->bind_param('s', $cardKey);
    
    if ($stmt->execute()) {
        echo json_encode(['success' => true, 'message' => '删除成功']);
    } else {
        echo json_encode(['success' => false, 'message' => '删除失败']);
    }
    $stmt->close();
} else {
    echo json_encode(['success' => false, 'message' => '参数不完整']);
}

$conn->close();
exit;
?>
