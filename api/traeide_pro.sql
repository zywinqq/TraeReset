-- Trae 卡密管理系统数据库初始化
-- AI虎哥优化制作 | https://3se.cc
-- 版本: 5.29 | 更新日期: 2026.05.29
-- 
-- 使用方法：直接在 traide_pro 数据库中执行此文件

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ============================================
-- 1. 卡密表
-- ============================================
CREATE TABLE IF NOT EXISTS `cards` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `card_key` VARCHAR(50) NOT NULL COMMENT '卡密',
  `card_type` VARCHAR(20) DEFAULT 'normal' COMMENT '卡密类型(vip/normal/trial)',
  `expire_date` DATE DEFAULT NULL COMMENT '过期日期(空表示永久)',
  `bound_devices` TEXT COMMENT '已绑定的设备ID列表(JSON格式)',
  `max_devices` INT DEFAULT 1 COMMENT '最大可绑定设备数',
  `use_count` INT DEFAULT 0 COMMENT '使用次数',
  `max_uses` INT DEFAULT -1 COMMENT '最大使用次数(-1表示无限)',
  `status` ENUM('active', 'used', 'expired', 'invalid') DEFAULT 'active' COMMENT '状态',
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `last_use_time` DATETIME DEFAULT NULL COMMENT '最后使用时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_card_key` (`card_key`),
  KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='卡密表';

-- ============================================
-- 2. 操作日志表
-- ============================================
CREATE TABLE IF NOT EXISTS `operation_logs` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `action` VARCHAR(50) NOT NULL COMMENT '操作类型',
  `card_key` VARCHAR(50) DEFAULT NULL COMMENT '涉及的卡密',
  `machine_id` VARCHAR(100) DEFAULT NULL COMMENT '设备ID',
  `ip_address` VARCHAR(50) DEFAULT NULL COMMENT 'IP地址',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
  PRIMARY KEY (`id`),
  KEY `idx_log_action` (`action`),
  KEY `idx_log_created` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='操作日志表';

-- ============================================
-- 3. 插入示例卡密数据(可选)
-- ============================================
INSERT INTO `cards` (`card_key`, `card_type`, `expire_date`, `max_devices`, `max_uses`) VALUES
('TRAE-2026-0001', 'vip', '2027-12-31', 3, 10),
('TRAE-2026-0002', 'vip', '2027-12-31', 3, 10),
('TRAE-2026-0003', 'normal', NULL, 1, 5),
('TRAE-2026-0004', 'normal', '2026-12-31', 1, -1),
('TRAE-2026-0005', 'trial', '2026-06-30', 1, 3);

SET FOREIGN_KEY_CHECKS = 1;

-- ============================================
-- 导入完成提示
-- ============================================
-- 数据库表创建成功！
-- 请确认以下配置与您的 config.php 一致：
-- DB_HOST: localhost
-- DB_USER: traeide_pro
-- DB_NAME: traeide_pro
-- ============================================
