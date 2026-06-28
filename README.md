# 🏢 企业私有化生成式AI平台

> Enterprise RAG Knowledge Base Platform — 基于 RAG 技术的企业内部 AI 智能问答平台

[![CI](https://github.com/YOUR_USERNAME/enterprise-rag-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/enterprise-rag-platform/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Vue 3](https://img.shields.io/badge/vue-3.x-brightgreen.svg)](https://vuejs.org/)

---

## ✨ 功能亮点

- 🔍 **RAG 智能问答** — 基于企业知识库的精准回答，带来源引用
- 📄 **多格式文档解析** — PDF、Word、Markdown、TXT 四种格式
- 🔐 **部门级权限控制** — 管理员/普通用户 + 文档可见性（公开/部门/受限）
- 💬 **流式对话** — SSE 实时流式输出，多轮对话上下文记忆
- 🤖 **Agent 系统** — 内置 Web 搜索、自动标签、审计日志
- 📊 **管理仪表盘** — ECharts 可视化统计、用户/部门/分类管理
- 🎨 **暗色主题** — 精致极简设计系统，企业级视觉风格
- 🐳 **Docker 一键部署** — `docker compose up -d` 启动全部服务

---

## 🏗️ 技术架构

```
┌─────────────────────────────────────────────────────┐
│                     Nginx (Port 80)                   │
│             前端静态资源 + API 反向代理 + SSE          │
└──────┬──────────────────────────────────┬────────────┘
       │                                  │
┌──────▼────────┐                 ┌──────▼────────────┐
│  Frontend     │                 │  Backend (Port 8000)│
│  Vue 3 + Vite │  ──HTTP/SSE──▶  │  FastAPI + LangChain│
│  Element Plus │                 │  SQLAlchemy 2.0     │
│  Pinia + ECharts│               │  DeepSeek Chat API  │
└───────────────┘                 └──┬──────┬───────┬──┘
                                     │      │       │
                              ┌──────▼──┐ ┌─▼────┐ ┌▼──────┐
                              │ MySQL 8 │ │Redis │ │Chroma │
                              │ (数据)  │ │(缓存)│ │(向量) │
                              └─────────┘ └──────┘ └───────┘
```

### 技术栈

| 层次 | 技术 |
|------|------|
| 前端 | Vue 3 + Vite + Element Plus + Pinia + ECharts + Marked |
| 后端 | FastAPI + SQLAlchemy 2.0 async + Celery + Loguru |
| AI | LangChain + LangGraph + DeepSeek Chat API |
| 向量库 | Chroma + ONNX all-MiniLM-L6-v2（本地嵌入，无需API） |
| 数据库 | MySQL 8.0 + Redis 7 |
| 认证 | JWT (python-jose) + bcrypt |
| 部署 | Docker + Nginx + docker-compose |
| CI/CD | GitHub Actions (lint → test → build) |
| 测试 | pytest + pytest-asyncio (SQLite 内存数据库) |

---

## 🚀 快速开始

### Docker 方式（推荐）

```bash
# 1. 克隆仓库
git clone https://github.com/YOUR_USERNAME/enterprise-rag-platform.git
cd enterprise-rag-platform

# 2. 配置环境变量
cp .env.docker .env
# 编辑 .env，填入: DEEPSEEK_API_KEY, JWT_SECRET, MYSQL_PASSWORD

# 3. 一键启动
docker compose up -d

# 4. 访问
# 前端: http://localhost
# API 文档: http://localhost:8000/api/docs
# 健康检查: http://localhost:8000/api/health
```

### 手动方式

```bash
# 1. 环境要求: Python 3.10+, Node.js 18+, MySQL 8.0
# 2. 创建数据库
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS rag_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -u root -p rag_platform < scripts/init_db.sql

# 3. 启动后端
cd backend
cp .env.example .env  # 编辑 .env 填入真实配置
poetry install --no-root
poetry run alembic upgrade head
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 4. 启动前端（另开终端）
cd frontend
npm install
npm run dev  # 访问 http://localhost:5173
```

### Make 命令

```bash
make help          # 查看所有命令
make dev           # 启动开发服务
make test          # 运行测试
make test-cov      # 测试 + 覆盖率报告
make lint          # 代码检查
make format        # 代码格式化
make docker-up     # Docker 部署
make docker-down   # 停止 Docker
```

---

## 📋 API 端点一览

### 认证
| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| POST | `/api/auth/register` | 用户注册 | 公开 |
| POST | `/api/auth/login` | 用户登录 | 公开 |
| POST | `/api/auth/refresh` | 刷新 Token | 认证 |
| POST | `/api/auth/logout` | 登出 | 认证 |

### 文档管理
| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| POST | `/api/documents/upload` | 上传文档 | 管理员 |
| GET | `/api/documents/` | 文档列表 | 认证 |
| GET | `/api/documents/{id}` | 文档详情 | 认证 |
| DELETE | `/api/documents/{id}` | 删除文档 | 管理员 |

### AI 问答
| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| POST | `/api/chat/send` | 发送消息（SSE 流式） | 认证 |
| GET | `/api/conversations/` | 对话列表 | 认证 |
| DELETE | `/api/conversations/{id}` | 删除对话 | 认证 |

### 管理
| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| CRUD | `/api/departments/` | 部门管理 | 管理员 |
| CRUD | `/api/users/` | 用户管理 | 管理员 |
| CRUD | `/api/categories/` | 分类管理 | 管理员 |
| GET | `/api/stats/` | 统计面板 | 管理员 |
| GET | `/api/audit-logs/` | 审计日志 | 管理员 |
| GET | `/api/export/` | 数据导出 | 管理员 |

> 完整 API 文档: http://localhost:8000/api/docs (Swagger UI)

---

## 📁 项目结构

```
enterprise-rag-platform/
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── api/                # 12个 API 路由模块
│   │   ├── models/             # SQLAlchemy ORM 模型
│   │   ├── schemas/            # Pydantic 请求/响应模型
│   │   ├── services/           # 业务逻辑层
│   │   ├── rag/                # RAG 核心 (Loader/Splitter/Embedder/Retriever/Generator/Agent)
│   │   ├── middleware/         # JWT 认证 + 审计中间件
│   │   └── utils/              # Loguru 日志配置
│   ├── alembic/                # 数据库迁移脚本
│   ├── tests/                  # pytest 测试 (26 cases)
│   ├── uploads/                # 上传文件存储
│   └── pyproject.toml          # Poetry 依赖管理
├── frontend/                   # Vue 3 前端
│   └── src/
│       ├── views/              # 7个页面 (登录/注册/问答/历史/文档/部门/管理)
│       ├── components/         # 通用组件
│       ├── stores/             # Pinia 状态管理
│       ├── router/             # 路由 + 权限守卫
│       └── api/                # Axios + JWT 拦截器
├── nginx/                      # Nginx 配置 (本地 + Docker)
├── .github/workflows/          # CI/CD Pipeline
├── scripts/                    # 初始化脚本
├── docs/                       # 8份技术文档
├── devlog/                     # 开发日志
├── docker-compose.yml          # Docker Compose 编排
├── backend/Dockerfile          # 后端 Docker 镜像
├── frontend/Dockerfile         # 前端 Docker 镜像
├── Makefile                    # 便捷命令
├── CHANGELOG.md                # 版本变更
└── LICENSE                     # MIT License
```

---

## 🧪 测试

```bash
cd backend
poetry run pytest tests/ -v          # 26 测试
poetry run pytest tests/ -v --cov    # 含覆盖率
```

---

## 📖 文档

| 文档 | 说明 |
|------|------|
| [开发需求规格](docs/01-开发需求规格.md) | 功能需求详情 |
| [技术选型与架构](docs/02-技术选型与架构设计.md) | 技术选型说明 |
| [前端设计规范](docs/03-前端设计规范.md) | 前端设计系统 |
| [后端开发规范](docs/04-后端开发规范.md) | 后端代码规范 |
| [API接口规范](docs/05-API接口规范.md) | 接口文档 |
| [数据库设计](docs/06-数据库设计规范.md) | 表结构与存储 |
| [AI Pipeline](docs/07-AI-Pipeline设计规范.md) | RAG 设计 |
| [执行步骤](docs/08-开发执行步骤.md) | 开发进度 |

---

## 📝 License

MIT License — 详见 [LICENSE](LICENSE)
