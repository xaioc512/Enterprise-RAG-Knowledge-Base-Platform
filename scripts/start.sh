#!/bin/bash
# ============================================
# 企业AI知识库平台 — 启动脚本
# ============================================

set -e

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

echo "=========================================="
echo "  企业AI知识库平台 - 启动"
echo "=========================================="

# 1. 检查依赖
echo ""
echo "[1/4] 检查环境..."
command -v python3 >/dev/null 2>&1 || { echo "ERROR: Python3 未安装"; exit 1; }
command -v node >/dev/null 2>&1 || { echo "ERROR: Node.js 未安装"; exit 1; }
command -v mysql >/dev/null 2>&1 || { echo "WARN: MySQL 客户端未安装，请确保MySQL服务运行中"; }
echo "  Python: $(python3 --version)"
echo "  Node:   $(node --version)"

# 2. 后端启动
echo ""
echo "[2/4] 启动后端服务..."
cd "$BACKEND_DIR"

# 检查 .env 文件
if [ ! -f .env ]; then
    echo "ERROR: backend/.env 文件不存在，请先配置环境变量"
    exit 1
fi

# 安装依赖（首次运行）
if [ ! -d ".venv" ] && ! poetry env info >/dev/null 2>&1; then
    echo "  安装Python依赖..."
    poetry install --no-root
fi

# 运行数据库迁移
echo "  运行数据库迁移..."
poetry run alembic upgrade head || echo "  WARN: 迁移失败，可能数据库未启动"

# 启动后端
echo "  启动FastAPI (port 8000)..."
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2 &
BACKEND_PID=$!
echo "  后端 PID: $BACKEND_PID"

# 3. 前端构建
echo ""
echo "[3/4] 构建前端..."
cd "$FRONTEND_DIR"
if [ ! -d "node_modules" ]; then
    echo "  安装前端依赖..."
    npm install
fi
echo "  构建..."
npm run build

# 4. Nginx 检查
echo ""
echo "[4/4] Nginx 配置..."
if command -v nginx >/dev/null 2>&1; then
    echo "  测试Nginx配置..."
    nginx -t -c "$PROJECT_DIR/nginx/nginx.conf" && nginx -s reload || echo "  WARN: Nginx 配置测试失败"
else
    echo "  WARN: Nginx 未安装，跳过"
    echo "  你可以直接访问: http://localhost:8000/api/docs (后端API)"
    echo "  前端开发模式: cd frontend && npm run dev"
fi

echo ""
echo "=========================================="
echo "  启动完成！"
echo "  前端: http://localhost (需Nginx)"
echo "  API:  http://localhost:8000/api/docs"
echo "  后端日志: $BACKEND_DIR/logs/"
echo "=========================================="

# 等待后端进程
wait $BACKEND_PID
