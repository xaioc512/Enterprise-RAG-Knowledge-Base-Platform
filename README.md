# 企业私有化生成式AI平台

基于 RAG（检索增强生成）技术的企业内部知识库 AI 智能问答平台。

## 技术栈

| 层次 | 技术 |
|------|------|
| 前端 | Vue 3 + Vite + Element Plus + Pinia |
| 后端 | FastAPI (Python 3.10+) + SQLAlchemy 2.0 async |
| AI | LangChain + DeepSeek Chat API |
| 向量库 | Chroma + ONNX all-MiniLM-L6-v2（本地嵌入） |
| 数据库 | MySQL 8.0 + Redis |
| 认证 | JWT (python-jose) + bcrypt |
| 反向代理 | Nginx |

## 快速开始

### 1. 环境要求

- Python 3.10+
- Node.js 18+
- MySQL 8.0
- Nginx（可选，也可直接访问后端）

### 2. 数据库初始化

```bash
# 创建数据库
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS rag_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 导入初始分类
mysql -u root -p rag_platform < scripts/init_db.sql
```

### 3. 后端配置

```bash
cd backend

# 安装依赖
pip install poetry  # 如果没有安装
poetry install --no-root

# 配置环境变量（编辑 .env 文件）
cp .env.example .env  # 如需要
# 必须修改: MYSQL_PASSWORD, JWT_SECRET

# 运行数据库迁移
poetry run alembic upgrade head

# 启动后端
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. 前端配置

```bash
cd frontend

# 安装依赖
npm install

# 开发模式（带热重载，API代理到 localhost:8000）
npm run dev

# 生产构建
npm run build
```

### 5. Nginx 部署（可选）

```bash
# 编辑 nginx/nginx.conf 中的 root 路径
# 替换 /path/to/project_3_agent_v2 为实际路径

nginx -t -c /path/to/nginx/nginx.conf
nginx -s reload
```

### 6. 一键启动

```bash
bash scripts/start.sh
```

## 项目结构

```
project_3_agent_v2/
├── backend/              # FastAPI 后端
│   ├── app/
│   │   ├── api/          # API 路由（8个模块）
│   │   ├── models/       # SQLAlchemy ORM（7张表）
│   │   ├── schemas/      # Pydantic 模型
│   │   ├── services/     # 业务逻辑层
│   │   ├── rag/          # RAG 核心模块
│   │   ├── middleware/   # JWT 认证中间件
│   │   └── utils/        # 工具（Loguru 日志）
│   ├── alembic/          # 数据库迁移
│   ├── uploads/          # 文档存储
│   └── .env              # 环境变量
├── frontend/             # Vue 3 前端
│   └── src/
│       ├── views/        # 页面（6个）
│       ├── components/   # 组件
│       ├── stores/       # Pinia 状态
│       ├── router/       # 路由 + 守卫
│       └── api/          # Axios + JWT
├── nginx/                # Nginx 配置
├── scripts/              # 脚本
├── docs/                 # 开发文档（8份）
├── devlog/               # 开发日志
└── CLAUDE.md             # 项目指引
```

## API 端点（25个）

详细文档：http://localhost:8000/api/docs (Swagger UI)

## 默认账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | 通过注册创建，然后在数据库中将 role 改为 admin |
| 用户 | 自行注册 | — |

## 文档

- [开发需求规格](docs/01-开发需求规格.md)
- [技术选型与架构](docs/02-技术选型与架构设计.md)
- [前端设计规范](docs/03-前端设计规范.md)
- [后端开发规范](docs/04-后端开发规范.md)
- [API接口规范](docs/05-API接口规范.md)
- [数据库设计](docs/06-数据库设计规范.md)
- [AI Pipeline](docs/07-AI-Pipeline设计规范.md)
- [执行步骤](docs/08-开发执行步骤.md)
