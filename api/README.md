# Trae Resetter 卡密验证API系统

## 📦 项目概述

这是一个完整的卡密验证API系统，使用 PHP + MySQL 开发，用于验证和管理 Trae Resetter 软件的卡密授权。

## 📁 文件结构

```
api/
├── index.php          # 管理员后台管理页面
├── check_card.php     # 卡密验证API（核心）
├── database.sql       # 数据库初始化脚本
├── stats.php          # 获取统计数据
├── get_cards.php      # 获取卡密列表
├── search_cards.php   # 搜索卡密
├── recent_logs.php    # 获取最近使用记录
├── get_logs.php       # 获取操作日志
├── generate_cards.php # 生成卡密
└── delete_card.php    # 删除卡密
```

## 🚀 快速部署

### 1. 环境要求
- PHP 7.4+
- MySQL 5.7+
- Apache/Nginx 服务器

### 2. 数据库配置

#### 2.1 创建数据库
```sql
CREATE DATABASE trae_card CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

#### 2.2 执行初始化脚本
```bash
mysql -u root -p trae_card < database.sql
```

#### 2.3 修改配置文件
编辑以下文件，修改数据库连接信息：
- `check_card.php`
- `stats.php`
- `get_cards.php`
- `search_cards.php`
- `recent_logs.php`
- `get_logs.php`
- `generate_cards.php`
- `delete_card.php`

配置示例：
```php
define('DB_HOST', 'localhost');
define('DB_USER', 'root');
define('DB_PASS', 'your_password');
define('DB_NAME', 'trae_card');
```

### 3. 部署到服务器

将 `api/` 目录上传到您的Web服务器（如 Apache/Nginx）。

示例路径：
```
https://api.3se.cc/trae/
```

### 4. 访问后台管理

打开浏览器访问：
```
https://api.3se.cc/trae/index.php
```

默认管理员账号：
- 用户名：`admin`
- 密码：`admin123`

## 🔌 API接口说明

### 1. 卡密验证接口

**地址**: `POST /check_card.php`

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| card_key | string | 是 | 卡密兑换码 |
| machine_id | string | 否 | 设备ID（用于绑定） |

**响应**:
```json
{
    "success": true,
    "message": "验证成功",
    "expire_date": "2027-12-31",
    "card_type": "vip",
    "use_count": 1
}
```

### 2. 获取统计数据

**地址**: `GET /stats.php`

**响应**:
```json
{
    "total": 100,
    "active": 85,
    "used": 10,
    "expired": 5
}
```

### 3. 获取卡密列表

**地址**: `GET /get_cards.php`

**响应**:
```json
[
    {
        "id": 1,
        "card_key": "TRAE-2026-0001",
        "card_type": "vip",
        "expire_date": "2027-12-31",
        "machine_id": null,
        "use_count": 0,
        "status": "active"
    }
]
```

### 4. 搜索卡密

**地址**: `GET /search_cards.php?key=xxx&status=xxx`

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| key | string | 否 | 搜索关键词 |
| status | string | 否 | 状态筛选 |

### 5. 生成卡密

**地址**: `POST /generate_cards.php`

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| count | int | 是 | 生成数量 |
| type | string | 是 | 卡密类型 |
| days | int | 否 | 有效期天数 |
| maxUses | int | 否 | 最大使用次数 |

### 6. 删除卡密

**地址**: `POST /delete_card.php`

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| card_key | string | 是 | 卡密 |

## 📊 数据库结构

### cards 表（卡密表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键ID |
| card_key | VARCHAR(50) | 卡密（唯一） |
| card_type | VARCHAR(20) | 卡密类型 |
| expire_date | DATE | 过期日期 |
| machine_id | VARCHAR(100) | 绑定设备ID |
| use_count | INT | 使用次数 |
| max_uses | INT | 最大使用次数 |
| status | ENUM | 状态（active/used/expired/invalid） |
| create_time | DATETIME | 创建时间 |
| bind_time | DATETIME | 绑定时间 |
| last_use_time | DATETIME | 最后使用时间 |

### admins 表（管理员表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键ID |
| username | VARCHAR(50) | 用户名 |
| password | VARCHAR(255) | 密码（MD5） |
| create_time | DATETIME | 创建时间 |

### operation_logs 表（操作日志表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键ID |
| action | VARCHAR(50) | 操作类型 |
| card_key | VARCHAR(50) | 涉及卡密 |
| machine_id | VARCHAR(100) | 设备ID |
| ip_address | VARCHAR(50) | IP地址 |
| created_at | DATETIME | 操作时间 |

## 🔒 安全建议

1. **修改默认密码**：部署后立即修改管理员密码
2. **HTTPS加密**：使用SSL证书，强制HTTPS访问
3. **IP白名单**：限制API访问IP
4. **请求频率限制**：防止恶意请求
5. **日志监控**：定期检查操作日志

## 📝 使用说明

### 客户端调用示例（Python）

```python
import requests

def check_card(card_key, machine_id):
    response = requests.post(
        'https://api.3se.cc/trae/check_card.php',
        {
            'card_key': card_key,
            'machine_id': machine_id
        }
    )
    return response.json()
```

### 生成卡密

1. 访问管理后台
2. 点击"生成卡密"标签
3. 设置生成数量、类型、有效期
4. 点击"生成卡密"按钮
5. 复制生成的卡密

### 管理卡密

- **搜索**：在卡密管理页面输入关键词搜索
- **筛选**：按状态筛选卡密
- **删除**：点击删除按钮移除卡密

## 📈 功能特性

- ✅ 卡密验证与绑定
- ✅ 设备绑定限制
- ✅ 有效期管理
- ✅ 使用次数限制
- ✅ 统计数据展示
- ✅ 操作日志记录
- ✅ 批量生成卡密
- ✅ 后台管理界面

## ⚠️ 注意事项

1. 请妥善保管卡密数据，定期备份数据库
2. 建议设置数据库访问权限，只允许特定IP访问
3. 定期清理过期和已使用的卡密记录
4. 监控API调用次数，防止恶意攻击

---

**© 2026 AI虎哥优化制作 | https://3se.cc**
**版本: 5.29 | 更新日期: 2026.05.29**
