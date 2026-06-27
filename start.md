# 后端
cd backend && poetry run uvicorn app.main:app --port 8000

# 前端（开发模式）
cd frontend && npm run dev

# 一键部署
bash scripts/start.sh
