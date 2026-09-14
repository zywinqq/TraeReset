<?php
/**
 * Trae 卡密管理系统 - 管理后台
 * AI虎哥优化制作 | https://3se.cc
 * 版本: 5.29 | 更新日期: 2026.05.29
 */
?>
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Trae 卡密管理系统 - AI虎哥优化制作</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            color: #333;
        }
        .container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            width: 90%;
            max-width: 1200px;
            padding: 30px;
            backdrop-filter: blur(10px);
        }
        .login-page {
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 40px 0;
        }
        .login-page h1 {
            font-size: 28px;
            color: #667eea;
            margin-bottom: 10px;
        }
        .login-page .subtitle {
            color: #666;
            margin-bottom: 30px;
        }
        .login-page input[type="password"] {
            width: 300px;
            padding: 12px 16px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            margin-bottom: 16px;
            transition: border-color 0.3s;
        }
        .login-page input[type="password"]:focus {
            outline: none;
            border-color: #667eea;
        }
        .login-btn {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 12px 40px;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .login-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
        }
        .login-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        .error-msg {
            color: #e74c3c;
            margin-top: 16px;
            display: none;
        }
        .admin-page { display: none; }
        .admin-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 16px;
            border-bottom: 1px solid #e0e0e0;
        }
        .admin-header h2 {
            font-size: 24px;
            color: #667eea;
        }
        .nav-tabs {
            display: flex;
            gap: 8px;
            margin-bottom: 20px;
        }
        .nav-tab {
            padding: 10px 20px;
            background: #f5f5f5;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.2s;
        }
        .nav-tab:hover { background: #e8e8e8; }
        .nav-tab.active {
            background: #667eea;
            color: white;
        }
        .tab-content { display: none; }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 16px;
            margin-bottom: 24px;
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
        }
        .stat-card.online {
            background: linear-gradient(135deg, #11998e, #38ef7d);
        }
        .stat-card .value {
            font-size: 32px;
            font-weight: bold;
        }
        .stat-card .label {
            font-size: 14px;
            opacity: 0.9;
            margin-top: 4px;
        }
        .section {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
        }
        .section h3 {
            font-size: 18px;
            margin-bottom: 16px;
            color: #667eea;
        }
        .form-row {
            display: flex;
            gap: 12px;
            margin-bottom: 12px;
            flex-wrap: wrap;
        }
        .form-row input, .form-row select {
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 14px;
        }
        .btn {
            padding: 8px 16px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.2s;
        }
        .btn-primary {
            background: #667eea;
            color: white;
        }
        .btn-primary:hover { background: #5a6fd6; }
        .btn-danger {
            background: #e74c3c;
            color: white;
        }
        .btn-danger:hover { background: #c0392b; }
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 12px;
        }
        table th, table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }
        table th {
            background: #f5f5f5;
            font-weight: 600;
        }
        .status-badge {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
        }
        .status-active { background: #d4edda; color: #155724; }
        .status-used { background: #cce5ff; color: #004085; }
        .status-expired { background: #f8d7da; color: #721c24; }
        .status-invalid { background: #e2e3e5; color: #383d41; }
        .status-inactive { background: #fff3cd; color: #856404; }
        .online-dot {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #38ef7d;
            margin-right: 4px;
            animation: pulse 1.5s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.4; }
        }
        textarea {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-family: monospace;
            font-size: 14px;
            resize: vertical;
            min-height: 100px;
        }
        .footer {
            text-align: center;
            color: #999;
            font-size: 12px;
            margin-top: 20px;
            padding-top: 16px;
            border-top: 1px solid #e0e0e0;
        }
        .logout-btn {
            background: #e74c3c;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
        }
        .pagination {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 8px;
            margin-top: 16px;
        }
        .pagination button {
            padding: 6px 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            background: white;
            cursor: pointer;
            font-size: 13px;
        }
        .pagination button:hover { background: #667eea; color: white; }
        .pagination button.active { background: #667eea; color: white; }
        .pagination button:disabled { opacity: 0.4; cursor: not-allowed; }
        .pagination .page-info { font-size: 13px; color: #666; }
        .page-jump { display: flex; align-items: center; gap: 4px; margin-left: 12px; }
        .page-jump input { width: 48px; padding: 4px 6px; border: 1px solid #ddd; border-radius: 4px; font-size: 13px; text-align: center; }
        .page-jump button { padding: 6px 10px; border: 1px solid #ddd; border-radius: 4px; background: white; cursor: pointer; font-size: 13px; }
        .page-jump button:hover { background: #667eea; color: white; }
        .status-badge-online { display: inline-block; width: 6px; height: 6px; border-radius: 50%; background: #38ef7d; margin-right: 4px; animation: pulse 1.5s infinite; }
        .online-dot-card { background: #e8f9e8; padding: 2px 8px; border-radius: 4px; font-size: 12px; color: #28a745; }
        .offline-dot-card { background: #f0f0f0; padding: 2px 8px; border-radius: 4px; font-size: 12px; color: #999; }
    </style>
</head>
<body>
    <div class="container">
        <div id="login-page" class="login-page">
            <h1>Trae 卡密管理系统</h1>
            <p class="subtitle">AI虎哥优化制作 | https://3se.cc</p>
            <input type="password" id="admin-password" placeholder="请输入管理密码">
            <button class="login-btn" onclick="doLogin()">登 录</button>
            <div id="error-msg" class="error-msg">密码错误，请重试</div>
            <div id="net-error" class="error-msg">网络请求失败，请检查连接</div>
        </div>

        <div id="admin-page" class="admin-page">
            <div class="admin-header">
                <h2>Trae 卡密管理后台</h2>
                <button class="logout-btn" onclick="doLogout()">退出登录</button>
            </div>

            <div class="nav-tabs">
                <button class="nav-tab active" onclick="showTab('dashboard')">数据总览</button>
                <button class="nav-tab" onclick="showTab('cards')">卡密管理</button>
                <button class="nav-tab" onclick="showTab('generate')">生成卡密</button>
                <button class="nav-tab" onclick="showTab('settings')">系统设置</button>
            </div>

            <div id="dashboard" class="tab-content" style="display:block">
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="value" id="stat-total">0</div>
                        <div class="label">卡密总数</div>
                    </div>
                    <div class="stat-card">
                        <div class="value" id="stat-active">0</div>
                        <div class="label">已激活</div>
                    </div>
                    <div class="stat-card" style="background:linear-gradient(135deg,#f5af19,#f12711)">
                        <div class="value" id="stat-inactive">0</div>
                        <div class="label">未激活</div>
                    </div>
                    <div class="stat-card" style="background:linear-gradient(135deg,#4facfe,#00f2fe)">
                        <div class="value" id="stat-used">0</div>
                        <div class="label">已使用</div>
                    </div>
                    <div class="stat-card" style="background:linear-gradient(135deg,#fa709a,#fee140)">
                        <div class="value" id="stat-expired">0</div>
                        <div class="label">已过期</div>
                    </div>
                </div>
                <div class="stats-grid" style="grid-template-columns:1fr;margin-top:-8px">
                    <div class="stat-card online">
                        <div class="value" id="stat-online">0</div>
                        <div class="label"><span class="online-dot"></span>在线设备</div>
                    </div>
                </div>

                <div class="section">
                    <h3>最近使用记录</h3>
                    <table id="recent-table">
                        <thead>
                            <tr><th>卡密</th><th>类型</th><th>设备ID</th><th>使用次数</th><th>使用时间</th><th>在线状态</th></tr>
                        </thead>
                        <tbody></tbody>
                    </table>
                </div>
            </div>

            <div id="cards" class="tab-content">
                <div class="section">
                    <h3>搜索卡密</h3>
                    <div class="form-row">
                        <input type="text" id="search-key" placeholder="输入卡密关键词">
                        <select id="filter-status">
                            <option value="">全部状态</option>
                            <option value="active">已激活</option>
                            <option value="used">已使用</option>
                            <option value="expired">已过期</option>
                        </select>
                        <button class="btn btn-primary" onclick="searchCards()">搜索</button>
                        <button class="btn btn-primary" onclick="loadCards(1)">刷新列表</button>
                    </div>
                </div>

                <div class="section">
                    <h3>卡密列表</h3>
                    <div class="form-row" style="margin-bottom:10px">
                        <button class="btn btn-primary" onclick="toggleAllCheckboxes()">全选/取消</button>
                        <button class="btn btn-danger" onclick="batchDelete()">批量删除</button>
                        <span id="selected-count" style="line-height:30px;color:#666;font-size:13px"></span>
                    </div>
                    <table id="cards-table">
                        <thead>
                            <tr><th style="width:40px"><input type="checkbox" id="select-all" onclick="toggleAllFromHeader(this)"></th><th>卡密</th><th>类型</th><th>到期时间</th><th>已绑设备</th><th>最大设备</th><th>使用次数</th><th>状态</th><th>操作</th></tr>
                        </thead>
                        <tbody></tbody>
                    </table>
                    <div class="pagination" id="pagination"></div>
                </div>
            </div>

            <div id="generate" class="tab-content">
                <div class="section">
                    <h3>批量生成卡密</h3>
                    <div class="form-row">
                        <input type="number" id="gen-count" value="10" min="1" max="1000" placeholder="生成数量">
                        <select id="gen-type">
                            <option value="normal">普通版</option>
                            <option value="pro">专业版</option>
                            <option value="enterprise">企业版</option>
                        </select>
                    </div>
                    <div class="form-row">
                        <input type="number" id="gen-days" value="365" min="-1" placeholder="有效天数(-1永久)">
                        <input type="number" id="gen-maxuses" value="-1" min="-1" placeholder="最大使用次数(-1不限)">
                        <input type="number" id="gen-maxdevices" value="1" min="1" placeholder="最大绑定设备数">
                    </div>
                    <button class="btn btn-primary" onclick="generateCards()">生成卡密</button>
                </div>

                <div class="section" id="gen-result" style="display:none">
                    <h3>生成的卡密</h3>
                    <textarea id="gen-output" readonly></textarea>
                </div>
            </div>

            <div id="settings" class="tab-content">
                <div class="section">
                    <h3>修改管理密码</h3>
                    <div class="form-row">
                        <input type="password" id="new-password" placeholder="新密码">
                        <input type="password" id="confirm-password" placeholder="确认新密码">
                        <button class="btn btn-primary" onclick="changePassword()">修改密码</button>
                    </div>
                </div>
            </div>

            <div class="footer">
                AI虎哥优化制作 | https://3se.cc | 版本 5.29 | 2026.05.29 更新
            </div>
        </div>
    </div>

    <script>
        var currentPage = 1;

        const API = {
            login: 'login.php',
            stats: 'stats.php',
            recentLogs: 'recent_logs.php',
            getCards: 'get_cards.php',
            searchCards: 'search_cards.php',
            generateCards: 'generate_cards.php',
            deleteCard: 'delete_card.php',
            editCard: 'edit_card.php',
            changePassword: 'change_password.php'
        };

        function apiPost(url, data) {
            return fetch(url, {
                method: 'POST',
                body: new URLSearchParams(data)
            }).then(function(r) { return r.json(); });
        }

        function apiGet(url) {
            return fetch(url).then(function(r) { return r.json(); });
        }

        function showError(id) {
            var el = document.getElementById(id);
            el.style.display = 'block';
            setTimeout(function() { el.style.display = 'none'; }, 3000);
        }

        function doLogin() {
            var pwd = document.getElementById('admin-password').value;
            if (!pwd) { alert('请输入密码'); return; }
            var btn = document.querySelector('.login-btn');
            btn.textContent = '登录中...';
            btn.disabled = true;

            apiPost(API.login, { action: 'login', password: pwd })
                .then(function(data) {
                    btn.textContent = '登 录';
                    btn.disabled = false;
                    if (data.success) {
                        document.getElementById('login-page').style.display = 'none';
                        document.getElementById('admin-page').style.display = 'block';
                        loadDashboard();
                    } else {
                        showError('error-msg');
                    }
                })
                .catch(function(err) {
                    btn.textContent = '登 录';
                    btn.disabled = false;
                    showError('net-error');
                });
        }

        function checkLogin() {
            apiPost(API.login, { action: 'check' }).then(function(data) {
                if (data.success) {
                    document.getElementById('login-page').style.display = 'none';
                    document.getElementById('admin-page').style.display = 'block';
                    loadDashboard();
                }
            }).catch(function() {});
        }

        function doLogout() {
            apiPost(API.login, { action: 'logout' }).then(function() {
                document.getElementById('login-page').style.display = 'flex';
                document.getElementById('admin-page').style.display = 'none';
                document.getElementById('admin-password').value = '';
            }).catch(function() {});
        }

        function showTab(tabId) {
            document.querySelectorAll('.nav-tab').forEach(function(t) { t.classList.remove('active'); });
            document.querySelectorAll('.tab-content').forEach(function(c) { c.style.display = 'none'; });
            var target = event.target;
            if (target && target.classList && target.classList.contains('nav-tab')) {
                target.classList.add('active');
            }
            document.getElementById(tabId).style.display = 'block';
            if (tabId === 'dashboard') loadDashboard();
            if (tabId === 'cards') loadCards(1);
        }

        function loadDashboard() {
            apiGet(API.stats).then(function(data) {
                document.getElementById('stat-total').textContent = data.total || 0;
                document.getElementById('stat-active').textContent = data.activated || 0;
                document.getElementById('stat-inactive').textContent = data.inactive || 0;
                document.getElementById('stat-used').textContent = data.used || 0;
                document.getElementById('stat-expired').textContent = data.expired || 0;
                document.getElementById('stat-online').textContent = data.online || 0;
            }).catch(function() {});

            apiGet(API.recentLogs).then(function(data) {
                var tbody = document.querySelector('#recent-table tbody');
                if (data && data.length > 0) {
                    tbody.innerHTML = data.map(function(item) {
                        var onlineHtml = item.is_online ? '<span class="online-dot-card"><span class="status-badge-online"></span>在线</span>' : '<span class="offline-dot-card">离线</span>';
                        return '<tr><td>' + item.card_key + '</td><td>' + item.card_type + '</td><td>' + (item.machine_id || '-') + '</td><td>' + item.use_count + '</td><td>' + item.last_use_time + '</td><td>' + onlineHtml + '</td></tr>';
                    }).join('');
                } else {
                    tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;color:#999">暂无记录</td></tr>';
                }
            }).catch(function() {});
        }

        function loadCards(page) {
            currentPage = page || 1;
            var url = API.getCards + '?page=' + currentPage + '&per_page=15';
            apiGet(url).then(function(data) {
                var tbody = document.querySelector('#cards-table tbody');
                var items = data.data || data;
                if (items && items.length > 0) {
                    tbody.innerHTML = items.map(function(item) {
                        var onlineBadge = item.is_online ? ' <span style="color:#28a745;font-size:11px">●在线</span>' : '';
                        var statusBadgeClass = item.display_status === '已激活' ? 'status-used' : item.display_status === '已使用' ? 'status-used' : item.display_status === '已过期' ? 'status-expired' : item.display_status === '已禁用' ? 'status-invalid' : item.display_status === '未激活' ? 'status-inactive' : 'status-active';
                        return '<tr><td><input type="checkbox" class="card-checkbox" value="' + item.card_key + '" onchange="updateSelectedCount()"></td><td>' + item.card_key + '</td><td>' + item.card_type + '</td><td>' + (item.expire_date || '永久') + '</td><td>' + (item.bound_devices || 0) + '</td><td>' + item.max_devices + '</td><td>' + item.use_count + '</td><td><span class="status-badge ' + statusBadgeClass + '">' + item.display_status + '</span>' + onlineBadge + '</td><td><button class="btn btn-primary" style="margin-right:4px;padding:4px 10px;font-size:12px" onclick="openEditModal(\'' + item.card_key + '\', \'' + item.card_type + '\', \'' + (item.expire_date || '') + '\', ' + item.max_devices + ', \'' + item.status + '\', ' + item.max_uses + ')">编辑</button><button class="btn btn-danger" style="padding:4px 10px;font-size:12px" onclick="deleteCard(\'' + item.card_key + '\')">删除</button></td></tr>';
                    }).join('');
                } else {
                    tbody.innerHTML = '<tr><td colspan="9" style="text-align:center;color:#999">暂无卡密</td></tr>';
                }
                renderPagination(data.pages || 0, currentPage);
            }).catch(function() {});
        }

        function renderPagination(totalPages, current) {
            if (totalPages <= 1) {
                document.getElementById('pagination').innerHTML = '';
                return;
            }
            var html = '<button ' + (current <= 1 ? 'disabled' : '') + ' onclick="loadCards(' + (current - 1) + ')">上一页</button>';
            var start = Math.max(1, current - 2);
            var end = Math.min(totalPages, current + 2);
            for (var i = start; i <= end; i++) {
                html += '<button class="' + (i === current ? 'active' : '') + '" onclick="loadCards(' + i + ')">' + i + '</button>';
            }
            html += '<button ' + (current >= totalPages ? 'disabled' : '') + ' onclick="loadCards(' + (current + 1) + ')">下一页</button>';
            html += '<span class="page-info">共' + totalPages + '页</span>';
            html += '<span class="page-jump"><input type="number" id="page-input" min="1" max="' + totalPages + '" value="' + current + '" onkeydown="if(event.keyCode===13)jumpToPage(' + totalPages + ')"> <button onclick="jumpToPage(' + totalPages + ')">跳转</button></span>';
            document.getElementById('pagination').innerHTML = html;
        }

        function jumpToPage(totalPages) {
            var input = document.getElementById('page-input');
            if (!input) return;
            var p = parseInt(input.value);
            if (p >= 1 && p <= totalPages) {
                loadCards(p);
            } else {
                alert('请输入1-' + totalPages + '之间的页码');
            }
        }

        function searchCards() {
            var key = document.getElementById('search-key').value;
            var status = document.getElementById('filter-status').value;
            var url = API.searchCards + '?key=' + encodeURIComponent(key) + '&status=' + encodeURIComponent(status);
            apiGet(url).then(function(data) {
                var tbody = document.querySelector('#cards-table tbody');
                var items = data.data || data;
                if (items && items.length > 0) {
                    tbody.innerHTML = items.map(function(item) {
                        var onlineBadge = item.is_online ? ' <span style="color:#28a745;font-size:11px">●在线</span>' : '';
                        var statusBadgeClass = item.display_status === '已激活' ? 'status-used' : item.display_status === '已过期' ? 'status-expired' : item.display_status === '已禁用' ? 'status-invalid' : 'status-active';
                        return '<tr><td><input type="checkbox" class="card-checkbox" value="' + item.card_key + '" onchange="updateSelectedCount()"></td><td>' + item.card_key + '</td><td>' + item.card_type + '</td><td>' + (item.expire_date || '永久') + '</td><td>' + (item.bound_devices || 0) + '</td><td>' + item.max_devices + '</td><td>' + item.use_count + '</td><td><span class="status-badge ' + statusBadgeClass + '">' + item.display_status + '</span>' + onlineBadge + '</td><td><button class="btn btn-primary" style="margin-right:4px;padding:4px 10px;font-size:12px" onclick="openEditModal(\'' + item.card_key + '\', \'' + item.card_type + '\', \'' + (item.expire_date || '') + '\', ' + item.max_devices + ', \'' + item.status + '\', ' + item.max_uses + ')">编辑</button><button class="btn btn-danger" style="padding:4px 10px;font-size:12px" onclick="deleteCard(\'' + item.card_key + '\')">删除</button></td></tr>';
                    }).join('');
                } else {
                    tbody.innerHTML = '<tr><td colspan="9" style="text-align:center;color:#999">未找到匹配的卡密</td></tr>';
                }
                document.getElementById('pagination').innerHTML = '';
            }).catch(function(e) { alert('搜索失败: ' + e.message); });
        }

        function generateCards() {
            var btn = event.target;
            var originalText = btn.textContent;
            btn.textContent = '生成中...';
            btn.disabled = true;

            apiPost(API.generateCards, {
                count: document.getElementById('gen-count').value,
                type: document.getElementById('gen-type').value,
                days: document.getElementById('gen-days').value,
                maxUses: document.getElementById('gen-maxuses').value,
                maxDevices: document.getElementById('gen-maxdevices').value
            }).then(function(data) {
                btn.textContent = originalText;
                btn.disabled = false;
                if (data && data.success) {
                    document.getElementById('gen-output').textContent = data.cards.join('\n');
                    document.getElementById('gen-result').style.display = 'block';
                } else {
                    alert('生成失败: ' + (data && data.message ? data.message : '未知错误'));
                }
            }).catch(function(e) {
                btn.textContent = originalText;
                btn.disabled = false;
                alert('请求失败: ' + e.message);
            });
        }

        function deleteCard(key) {
            if (!confirm('确定删除该卡密？')) return;
            apiPost(API.deleteCard, { card_key: key }).then(function(data) {
                alert(data.message || '操作完成');
                loadCards(currentPage);
            }).catch(function(e) { alert('删除失败: ' + e.message); });
        }

        function changePassword() {
            var pwd = document.getElementById('new-password').value;
            var confirmPwd = document.getElementById('confirm-password').value;
            if (!pwd || pwd !== confirmPwd) { alert('两次密码不一致'); return; }
            apiPost(API.changePassword, { new_password: pwd }).then(function(data) {
                alert(data.message || '操作完成');
                if (data.success) doLogout();
            }).catch(function(e) { alert('修改失败: ' + e.message); });
        }

        document.getElementById('admin-password').focus();

        function toggleAllCheckboxes() {
            var checkboxes = document.querySelectorAll('.card-checkbox');
            var allChecked = Array.from(checkboxes).every(function(cb) { return cb.checked; });
            checkboxes.forEach(function(cb) { cb.checked = !allChecked; });
            updateSelectedCount();
        }

        function toggleAllFromHeader(el) {
            var checkboxes = document.querySelectorAll('.card-checkbox');
            checkboxes.forEach(function(cb) { cb.checked = el.checked; });
            updateSelectedCount();
        }

        function batchDelete() {
            var checkboxes = document.querySelectorAll('.card-checkbox:checked');
            if (checkboxes.length === 0) { alert('请至少选择一张卡密'); return; }
            if (!confirm('确定删除选中的 ' + checkboxes.length + ' 张卡密？此操作不可恢复！')) return;
            var cardKeys = Array.from(checkboxes).map(function(cb) { return cb.value; });

            apiPost(API.deleteCard, { card_keys: JSON.stringify(cardKeys) })
                .then(function(data) {
                    alert(data.message || '操作完成');
                    loadCards(currentPage);
                }).catch(function(e) { alert('批量删除失败: ' + e.message); });
        }

        function updateSelectedCount() {
            var count = document.querySelectorAll('.card-checkbox:checked').length;
            document.getElementById('selected-count').textContent = count > 0 ? '已选择 ' + count + ' 张' : '';
        }

        function openEditModal(cardKey, cardType, expireDate, maxDevices, status, maxUses) {
            document.getElementById('edit-card-key').textContent = cardKey;
            document.getElementById('edit-card-type').value = cardType;
            document.getElementById('edit-expire-date').value = expireDate;
            document.getElementById('edit-max-devices').value = maxDevices;
            document.getElementById('edit-status').value = status;
            document.getElementById('edit-max-uses').value = maxUses !== null && maxUses !== undefined ? maxUses : -1;
            document.getElementById('edit-modal').style.display = 'flex';
        }

        function closeEditModal() {
            document.getElementById('edit-modal').style.display = 'none';
        }

        function saveCardEdit() {
            var cardKey = document.getElementById('edit-card-key').textContent;
            var cardType = document.getElementById('edit-card-type').value;
            var expireDate = document.getElementById('edit-expire-date').value;
            var maxDevices = document.getElementById('edit-max-devices').value;
            var status = document.getElementById('edit-status').value;
            var maxUses = document.getElementById('edit-max-uses').value;

            apiPost(API.editCard, {
                card_key: cardKey,
                card_type: cardType,
                expire_date: expireDate,
                max_devices: maxDevices,
                status: status,
                max_uses: maxUses
            }).then(function(data) {
                alert(data.message || '操作完成');
                if (data.success) {
                    closeEditModal();
                    loadCards(currentPage);
                }
            }).catch(function(e) { alert('修改失败: ' + e.message); });
        }

        // 点击模态框外部关闭
        document.addEventListener('click', function(e) {
            var modal = document.getElementById('edit-modal');
            if (modal && e.target === modal) {
                closeEditModal();
            }
        });

        // 页面加载时检查登录状态
        checkLogin();
    </script>

    <!-- 编辑卡密模态框 -->
    <div id="edit-modal" style="display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.5);z-index:1000;justify-content:center;align-items:center">
        <div style="background:#fff;border-radius:12px;padding:30px;width:420px;max-width:90%">
            <h3 style="margin-bottom:20px;color:#667eea;font-size:18px">编辑卡密属性</h3>
            <div style="margin-bottom:16px">
                <label style="display:block;margin-bottom:6px;font-weight:600;color:#555">卡密</label>
                <span id="edit-card-key" style="font-family:monospace;font-size:13px;color:#333;background:#f5f5f5;padding:8px 12px;border-radius:6px;display:block;word-break:break-all"></span>
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px">
                <div>
                    <label style="display:block;margin-bottom:6px;font-weight:600;color:#555">类型</label>
                    <select id="edit-card-type" style="width:100%;padding:10px;border:1px solid #ddd;border-radius:6px;font-size:14px">
                        <option value="normal">普通版</option>
                        <option value="pro">专业版</option>
                        <option value="enterprise">企业版</option>
                    </select>
                </div>
                <div>
                    <label style="display:block;margin-bottom:6px;font-weight:600;color:#555">状态</label>
                    <select id="edit-status" style="width:100%;padding:10px;border:1px solid #ddd;border-radius:6px;font-size:14px">
                        <option value="active">正常</option>
                        <option value="expired">已过期</option>
                        <option value="invalid">已禁用</option>
                    </select>
                </div>
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin-bottom:20px">
                <div>
                    <label style="display:block;margin-bottom:6px;font-weight:600;color:#555">到期日期</label>
                    <input type="date" id="edit-expire-date" style="width:100%;padding:10px;border:1px solid #ddd;border-radius:6px;font-size:14px">
                </div>
                <div>
                    <label style="display:block;margin-bottom:6px;font-weight:600;color:#555">最大设备数</label>
                    <input type="number" id="edit-max-devices" min="1" style="width:100%;padding:10px;border:1px solid #ddd;border-radius:6px;font-size:14px">
                </div>
                <div>
                    <label style="display:block;margin-bottom:6px;font-weight:600;color:#555">最大使用次数</label>
                    <input type="number" id="edit-max-uses" min="-1" placeholder="-1不限" style="width:100%;padding:10px;border:1px solid #ddd;border-radius:6px;font-size:14px">
                </div>
            </div>
            <div style="display:flex;justify-content:flex-end;gap:10px;margin-top:20px">
                <button onclick="closeEditModal()" style="padding:10px 24px;border:1px solid #ddd;background:#fff;color:#666;border-radius:6px;cursor:pointer;font-size:14px">取消</button>
                <button onclick="saveCardEdit()" style="padding:10px 24px;border:none;background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;border-radius:6px;cursor:pointer;font-size:14px">保存修改</button>
            </div>
        </div>
    </div>
</body>
</html>
