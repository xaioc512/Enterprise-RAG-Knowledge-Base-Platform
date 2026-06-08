-- ============================================
-- 企业AI知识库平台 — 数据库初始化脚本
-- 使用方法: mysql -u root -p < scripts/init_db.sql
-- ============================================

CREATE DATABASE IF NOT EXISTS rag_platform
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE rag_platform;

-- 默认管理员账号（密码: admin123，需通过应用注册后修改）
-- 实际用户通过应用注册/API创建
