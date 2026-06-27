# ============================================
# 企业AI知识库平台 — Makefile
# ============================================

.PHONY: help dev build test lint docker-up docker-down clean

# 默认目标
help: ## 显示帮助信息
	@echo "企业AI知识库平台 — 命令列表"
	@echo ""
	@awk -F ':|##' '/^[^\t].+:.*##/ {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$NF}' $(MAKEFILE_LIST)

# ═══════════════════════════════════════════
# 开发
# ═══════════════════════════════════════════

dev: ## 启动开发服务（后端 8000 + 前端 5173）
	@echo "Starting backend on :8000..."
	cd backend && poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
	@sleep 2
	@echo "Starting frontend on :5173..."
	cd frontend && npm run dev

dev-backend: ## 仅启动后端开发服务
	cd backend && poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

dev-frontend: ## 仅启动前端开发服务
	cd frontend && npm run dev

# ═══════════════════════════════════════════
# 构建
# ═══════════════════════════════════════════

build: ## 构建前端生产版本
	cd frontend && npm run build

install: ## 安装所有依赖
	cd backend && poetry install --no-root
	cd frontend && npm install

# ═══════════════════════════════════════════
# 测试
# ═══════════════════════════════════════════

test: ## 运行后端测试
	cd backend && poetry run pytest tests/ -v

test-cov: ## 运行测试并生成覆盖率报告
	cd backend && poetry run pytest tests/ -v --cov=app --cov-report=html --cov-report=term
	@echo "Coverage report: backend/htmlcov/index.html"

test-all: test ## 运行全部测试

# ═══════════════════════════════════════════
# 代码质量
# ═══════════════════════════════════════════

lint: ## 代码检查
	cd backend && poetry run ruff check app/ && poetry run ruff format --check app/
	@echo "Lint OK"

format: ## 代码格式化
	cd backend && poetry run ruff check --fix app/ && poetry run ruff format app/
	cd frontend && npx prettier --write src/

# ═══════════════════════════════════════════
# Docker
# ═══════════════════════════════════════════

docker-up: ## 启动 Docker Compose 服务
	docker compose up -d
	@echo "Services starting... frontend → http://localhost"

docker-down: ## 停止 Docker Compose 服务
	docker compose down

docker-logs: ## 查看 Docker 日志
	docker compose logs -f

docker-build: ## 构建 Docker 镜像
	docker compose build

# ═══════════════════════════════════════════
# 数据库
# ═══════════════════════════════════════════

db-migrate: ## 运行数据库迁移
	cd backend && poetry run alembic upgrade head

db-migrate-new: ## 创建新迁移 (usage: make db-migrate-new MSG="description")
	cd backend && poetry run alembic revision --autogenerate -m "$(MSG)"

# ═══════════════════════════════════════════
# 清理
# ═══════════════════════════════════════════

clean: ## 清理构建产物和缓存
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf backend/.pytest_cache backend/htmlcov backend/coverage.xml
	rm -rf frontend/dist frontend/node_modules/.vite
	@echo "Cleaned"
