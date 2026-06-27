# ============================================
# 企业AI知识库平台 — 前端 Dockerfile
# Node.js 18 构建 + Nginx 部署
# ============================================

# --- 构建阶段 ---
FROM node:18-alpine AS builder

WORKDIR /app

COPY frontend/package.json frontend/package-lock.json* ./

RUN npm ci

COPY frontend/ .

RUN npm run build

# --- 运行阶段 ---
FROM nginx:1.27-alpine

# 复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制 Nginx 配置
COPY nginx/nginx.docker.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
