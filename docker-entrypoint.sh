#!/bin/bash
# ============================================
# 后端 Docker 启动脚本
# 等待 MySQL 就绪 → 运行迁移 → 启动服务
# ============================================
set -e

echo ""
echo "========================================"
echo "  企业AI知识库平台 — 后端启动"
echo "========================================"
echo ""

# 等待 MySQL 就绪
echo "[1/3] 等待 MySQL 就绪..."
for i in $(seq 1 30); do
    if nc -z "$MYSQL_HOST" "${MYSQL_PORT:-3306}" 2>/dev/null; then
        echo "  MySQL 已就绪 ($MYSQL_HOST:${MYSQL_PORT:-3306})"
        break
    fi
    if [ "$i" = "30" ]; then
        echo "  ERROR: MySQL 启动超时，退出"
        exit 1
    fi
    echo "  等待中... ($i/30)"
    sleep 2
done

# 运行数据库迁移
echo ""
echo "[2/3] 运行数据库迁移..."
alembic upgrade head
echo "  迁移完成"

# 启动 FastAPI
echo ""
echo "[3/3] 启动 FastAPI (port ${PORT:-8000})..."
exec "$@"
