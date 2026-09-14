<?php
/**
 * 数据库配置文件
 * AI虎哥优化制作 | https://3se.cc
 * 版本: 5.29 | 更新日期: 2026.05.29
 *
 * ⚠️ 请修改下方数据库连接信息为你服务器的实际配置
 */

// ============================================
// 数据库连接配置
// ============================================
define('DB_HOST', 'localhost');    // 数据库地址
define('DB_USER', 'traeide_pro');         // 数据库用户名
define('DB_PASS', 'hhXxcaekkGxwsAKE');         // ️ 数据库密码 - 请修改为实际密码
define('DB_NAME', 'traeide_pro');    // 数据库名称

// ============================================
// 管理密码配置
// ============================================
define('ADMIN_PASSWORD', '2452937');        // 管理后台登录密码
define('ADMIN_PASSWORD_MD5', md5('2452937')); // 密码的MD5值

// ============================================
// API基础配置
// ============================================
define('API_VERSION', '5.29');
define('API_DATE', '2026-05-29');
define('API_AUTHOR', 'AI虎哥优化制作');
define('API_WEBSITE', 'https://3se.cc');

/**
 * 获取数据库连接
 * 使用 ping() 检测连接状态，确保返回的是可用连接
 * @return mysqli|null
 */
function get_db_connection() {
    static $conn = null;

    // 首次连接
    if ($conn === null) {
        $conn = new mysqli(DB_HOST, DB_USER, DB_PASS, DB_NAME);
        if ($conn->connect_error) {
            $conn = null;  // 连接失败，重置为 null 以便下次重试
            return null;
        }
        $conn->set_charset('utf8mb4');
        return $conn;
    }

    // 检测连接是否还活着（可能已被 close() 关闭或超时断开）
    if (!@$conn->ping()) {
        $conn = new mysqli(DB_HOST, DB_USER, DB_PASS, DB_NAME);
        if ($conn->connect_error) {
            $conn = null;
            return null;
        }
        $conn->set_charset('utf8mb4');
    }

    return $conn;
}

/**
 * 返回JSON响应
 */
function api_response($success, $message = '', $data = []) {
    $result = ['success' => $success, 'message' => $message];
    if (!empty($data)) {
        $result = array_merge($result, $data);
    }
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode($result, JSON_UNESCAPED_UNICODE);
    exit;
}

/**
 * 记录操作日志
 * 注意：此函数不抛出异常，日志失败不影响主流程
 */
function log_action($action, $card_key = '', $machine_id = '') {
    try {
        $conn = get_db_connection();
        if (!$conn) return;
        $ip = $_SERVER['REMOTE_ADDR'] ?? '';
        $stmt = @$conn->prepare("INSERT INTO operation_logs (action, card_key, machine_id, ip_address) VALUES (?, ?, ?, ?)");
        if ($stmt) {
            @$stmt->bind_param('ssss', $action, $card_key, $machine_id, $ip);
            @$stmt->execute();
            @$stmt->close();
        }
    } catch (\Throwable $e) {
        // 静默忽略日志错误，不影响主流程
        error_log('[log_action] ' . $e->getMessage());
    }
}
?>
