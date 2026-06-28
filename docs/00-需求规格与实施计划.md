# 企业私有化生成式AI平台 — 需求规格与实施计划

## 一、项目概述

构建一个企业内部私有化部署的生成式AI知识问答平台，基于RAG（检索增强生成）技术，将企业内部的制度规范、工艺流程、流程文档、技术文档等知识资产进行智能化管理，提供基于AI的多轮对话问答服务。

---

## 二、技术栈确认

| 层次 | 技术 | 说明 |
|------|------|------|
| 前端框架 | Vue 3 + Vite | SPA应用，与后端通过REST API通信 |
| UI组件库 | Element Plus | Vue 3 企业级UI组件库，中文生态成熟 |
| 状态管理 | Pinia | Vue 3 官方状态管理 |
| 后端框架 | FastAPI (Python 3.10+) | 高性能异步API框架，自动生成OpenAPI文档 |
| 依赖管理 | Poetry | Python依赖管理与锁定版本，替代 pip + requirements.txt |
| 异步任务 | Celery + Redis | 耗时任务（文档解析/向量化）异步后台处理 |
| ASGI服务 | Uvicorn + Gunicorn | 生产级ASGI服务器部署 |
| ORM & 迁移 | SQLAlchemy 2.0 (async) + Alembic | 异步数据库操作 + 版本化迁移 |
| AI Agent核心 | LangChain + LangGraph | RAG检索链 + 多轮对话Agent编排 |
| 大模型 | DeepSeek (API) | `sk-40b3170c140e449ebaa2ac937f62c084` |
| 主数据库 | MySQL 8.0 | 用户、文档元数据、对话历史、分类等结构化数据 |
| 缓存/队列 | Redis | 会话缓存 + Celery消息队列 |
| 向量库 | Chroma | RAG知识库，存储文档向量嵌入 |
| 工具链 | Pandas（数据分析）、Requests（联网/接口调用） |
| 结构化日志 | Loguru | JSON格式结构化日志，便于排查与对接日志平台 |
| 鉴权 | JWT (python-jose + passlib) | 用户认证与授权 |
| 反向代理 | Nginx | 前端静态资源 + API代理 |
| 部署 | 手动部署 | 各服务通过 systemd/supervisor 管理进程 |

---

## 三、用户角色与权限

### 3.1 角色定义（两级）

| 角色 | 权限 |
|------|------|
| **管理员** | 文档上传、文档管理（增删改查）、知识分类管理、用户管理、系统设置 |
| **普通用户** | AI问答、查看对话历史、对回答进行反馈（点赞/点踩）、预览文档 |

所有用户可访问全部知识库（无部门隔离）。

### 3.2 认证流程
- JWT Token 登录认证
- Token 过期刷新机制
- 前端路由守卫 + 后端中间件鉴权

---

## 四、功能模块（MVP）

### 4.1 管理后台（管理员）

#### 知识分类管理
- 四大预设分类：**制度规范**、**工艺流程**、**流程文档**、**技术文档**
- 支持分类的增删改查

#### 文档管理
- **手动上传**：支持 PDF、Word (.docx)、Markdown、TXT 四种格式
- **文档解析**：后端自动解析文档文本内容
- **分块入库**：解析后文本按语义分块 → 向量嵌入 → 存入 Chroma
- **文档预览**：上传后可在平台内预览原始文档内容（PDF内嵌渲染、Markdown渲染、文本展示）
- **文档CRUD**：文档的上传、查看、删除；关联分类和标签

### 4.2 用户端（所有用户）

#### AI智能问答
- **多轮对话**：支持上下文关联的连续追问，类似ChatGPT体验
- **RAG检索增强**：用户提问 → 向量检索相关文档片段 → 拼接上下文 → DeepSeek生成回答
- **引用溯源**：AI回答中标注信息来源，明确出自哪个文档的哪一段
- **Markdown渲染**：回答内容支持Markdown格式排版展示

#### 对话历史
- 用户可查看自己的历史对话记录
- 支持按时间倒序排列
- 可点击进入历史对话继续提问或查看详情

#### 反馈机制
- 每条AI回答支持**点赞/点踩**
- 反馈数据记录到数据库，用于后续评估知识库质量

### 4.3 通用功能
- 用户注册/登录/信息修改
- 用户管理（管理员进行用户增删改查）

---

## 五、系统架构

```
┌──────────────────────────────────────────────────────────┐
│                         Nginx                             │
│            (前端静态资源 + /api/* 反向代理)                  │
└──────┬──────────────────────┬────────────────────────────┘
       │                      │
       ▼                      ▼
┌──────────────┐   ┌───────────────────────────────────────┐
│  Vue 3 前端   │   │          FastAPI 后端                  │
│  (Element+)  │   │         (Uvicorn)                      │
│              │   │                                       │
│  - 登录/注册  │   │  ┌─ /api/auth (认证模块)               │
│  - 问答界面   │   │  ├─ /api/users (用户管理)              │
│  - 管理后台   │   │  ├─ /api/documents (文档管理)          │
│  - 对话历史   │   │  ├─ /api/categories (分类管理)         │
│              │   │  ├─ /api/chat (AI问答)                 │
│  - Pinia     │   │  └─ /api/feedback (反馈)               │
│    状态管理   │   │                                       │
└──────────────┘   │  ┌────────────────────────────────┐   │
                   │  │    LangChain RAG Pipeline       │   │
                   │  │    - 文档解析 & 分块             │   │
                   │  │    - 向量嵌入 & 存储             │   │
                   │  │    - 检索 & 重排序               │   │
                   │  │    - DeepSeek 生成 (流式)        │   │
                   │  └────────────────────────────────┘   │
                   │                                       │
                   │  ┌────────────────────────────────┐   │
                   │  │  Celery Worker (异步进程)        │   │
                   │  │  - 文档解析任务                  │   │
                   │  │  - 向量嵌入任务                  │   │
                   │  │  - 日志: Loguru                  │   │
                   │  └────────────────────────────────┘   │
                   └──┬────────┬─────────┬─────────────────┘
                      │        │         │
                      ▼        ▼         ▼
                 ┌──────┐ ┌──────┐ ┌──────────┐
                 │MySQL │ │Redis │ │ Chroma   │
                 │ 8.0  │ │      │ │(向量库)   │
                 └──────┘ └──────┘ └──────────┘
```

### 数据流（RAG问答流程）

```
用户提问 → JWT鉴权 → 问题向量化 → Chroma检索Top-K相关片段
    → 拼接检索上下文 + 对话历史 → DeepSeek生成回答
    → 保存对话记录 → 返回回答(含引用来源)
```

### 数据流（文档入库流程 — Celery异步）

```
管理员上传文档 → 保存原始文件 → 返回"处理中" → 提交Celery任务
    → Celery Worker: 文件类型检测 → 文本解析(按格式)
    → 文本智能分块 → DeepSeek Embedding → 向量存入Chroma
    → 更新MySQL文档状态为done → Loguru记录处理日志
```

---

## 六、数据库设计（核心表）

### MySQL 表结构

```sql
-- 用户表
users: id, username, password_hash, email, role(admin/user), created_at, updated_at

-- 知识分类表
categories: id, name, description, created_at

-- 文档表
documents: id, title, category_id, file_type, file_path, file_size,
           chunk_count, status(processing/done/error), uploaded_by, created_at, updated_at

-- 文档分块表
document_chunks: id, document_id, chunk_index, content, chunk_hash, created_at

-- 对话表
conversations: id, user_id, title, created_at, updated_at

-- 消息表
messages: id, conversation_id, role(user/assistant), content,
          sources(JSON, 引用来源), created_at

-- 反馈表
feedbacks: id, message_id, user_id, rating(like/dislike), created_at
```

### Redis 用途
- Celery 消息队列（Broker + Backend），驱动文档处理异步任务
- JWT Token 黑名单（登出失效）
- 用户会话缓存

### Chroma 存储
- Collection: `knowledge_base`
- 存储文档分块的向量嵌入（Embedding维度由DeepSeek模型决定）
- Metadata: document_id, chunk_index, category_id, title, source_text前200字

---

## 七、API接口设计（核心端点）

```
# 认证
POST   /api/auth/login          # 登录
POST   /api/auth/register       # 注册
POST   /api/auth/refresh        # 刷新Token
POST   /api/auth/logout         # 登出

# 用户管理（管理员）
GET    /api/users               # 用户列表
POST   /api/users               # 创建用户
PUT    /api/users/{id}          # 修改用户
DELETE /api/users/{id}          # 删除用户

# 知识分类
GET    /api/categories          # 分类列表
POST   /api/categories          # 创建分类
PUT    /api/categories/{id}     # 修改分类
DELETE /api/categories/{id}     # 删除分类

# 文档管理（管理员）
GET    /api/documents           # 文档列表（支持分类筛选）
POST   /api/documents/upload    # 上传文档
GET    /api/documents/{id}      # 文档详情
GET    /api/documents/{id}/preview  # 文档预览
DELETE /api/documents/{id}      # 删除文档
POST   /api/documents/{id}/reprocess  # 重新解析向量化

# AI问答
POST   /api/chat/send           # 发送消息（SSE流式响应）
GET    /api/chat/stream/{conv_id}  # 流式获取回答（SSE）

# 对话管理
GET    /api/conversations            # 对话列表
POST   /api/conversations            # 创建新对话
GET    /api/conversations/{id}       # 对话详情（含消息列表）
DELETE /api/conversations/{id}       # 删除对话
PUT    /api/conversations/{id}/title # 修改对话标题

# 反馈
POST   /api/feedback            # 提交反馈（点赞/点踩）

# 系统
GET    /api/health              # 健康检查
GET    /api/stats               # 统计信息（管理员）
```

---

## 八、项目目录结构

```
project_3_agent_v2/
├── frontend/                    # Vue 3 前端
│   ├── src/
│   │   ├── components/         # 复用组件
│   │   │   ├── ChatMessage.vue       # 聊天消息(含引用标注)
│   │   │   ├── DocumentPreview.vue   # 文档预览组件
│   │   │   ├── Sidebar.vue           # 侧边栏
│   │   │   └── ...
│   │   ├── views/              # 页面
│   │   │   ├── Login.vue             # 登录
│   │   │   ├── Register.vue          # 注册
│   │   │   ├── ChatView.vue          # 问答主界面
│   │   │   ├── HistoryView.vue       # 对话历史
│   │   │   ├── AdminDashboard.vue    # 管理后台首页
│   │   │   ├── DocumentManage.vue    # 文档管理
│   │   │   ├── CategoryManage.vue    # 分类管理
│   │   │   └── UserManage.vue        # 用户管理
│   │   ├── stores/             # Pinia 状态管理
│   │   ├── router/             # 路由配置
│   │   ├── api/                # API 请求封装
│   │   └── utils/              # 工具函数
│   ├── package.json
│   └── vite.config.js
│
├── backend/                     # FastAPI 后端
│   ├── pyproject.toml           # Poetry 依赖管理
│   ├── alembic/                 # 数据库迁移脚本
│   ├── alembic.ini
│   ├── app/
│   │   ├── main.py              # FastAPI 应用入口
│   │   ├── config.py            # 配置管理 (Pydantic Settings)
│   │   ├── database.py          # MySQL 异步连接 (AsyncSession)
│   │   ├── redis_client.py      # Redis 连接管理
│   │   ├── celery_app.py        # Celery 应用配置
│   │   ├── celery_worker.py     # Celery Worker 入口
│   │   ├── models/              # SQLAlchemy 数据模型
│   │   │   ├── user.py
│   │   │   ├── document.py
│   │   │   ├── conversation.py
│   │   │   └── feedback.py
│   │   ├── schemas/             # Pydantic 请求/响应模型
│   │   ├── api/                 # API 路由
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── documents.py
│   │   │   ├── categories.py
│   │   │   ├── chat.py
│   │   │   ├── conversations.py
│   │   │   └── feedback.py
│   │   ├── services/            # 业务逻辑层
│   │   │   ├── auth_service.py
│   │   │   ├── document_service.py
│   │   │   ├── chat_service.py
│   │   │   └── rag_service.py
│   │   ├── tasks/               # Celery 异步任务
│   │   │   ├── document_tasks.py     # 文档处理任务
│   │   │   └── embedding_tasks.py    # 向量化任务
│   │   ├── rag/                 # RAG 核心模块
│   │   │   ├── loader.py        # 文档加载器 (PDF/Word/MD/TXT)
│   │   │   ├── splitter.py      # 文本分块器
│   │   │   ├── embedder.py      # DeepSeek Embedding
│   │   │   ├── retriever.py     # Chroma检索器
│   │   │   ├── generator.py     # DeepSeek LLM生成
│   │   │   └── pipeline.py      # 完整RAG流水线编排
│   │   ├── middleware/          # 中间件
│   │   │   └── auth_middleware.py
│   │   └── utils/
│   │       └── logger.py        # Loguru 结构化日志配置
│
├── nginx/                       # Nginx 配置
│   └── nginx.conf
├── scripts/                     # 部署脚本
│   ├── init_db.sql              # 数据库初始化
│   └── start.sh                 # 启动脚本 (含 Celery Worker)
├── uploads/                     # 文档上传存储目录
└── README.md                    # 项目文档
```

---

## 九、AI Pipeline 设计

### 9.1 文档处理 Pipeline
```
上传文件 → 类型检测（pdf/docx/md/txt）
    → Loader加载（PyPDF2/python-docx/markdown/plaintext）
    → TextSplitter分块（RecursiveCharacterTextSplitter, chunk_size=500, overlap=50）
    → DeepSeek Embedding（批量向量化）
    → Chroma.add() 存储向量 + 元数据
    → 更新MySQL文档状态为done
```

### 9.2 RAG问答 Pipeline
```
用户问题 → JWT鉴权 → 获取/创建对话
    → DeepSeek Embedding(问题)
    → Chroma.similarity_search(query_embedding, k=5)
    → 构建Prompt模板（系统提示 + 检索上下文 + 对话历史 + 用户问题）
    → DeepSeek Chat API（流式生成）
    → 解析引用来源
    → 保存消息到MySQL
    → SSE流式返回前端
```

### 9.3 Prompt 模板设计
```
系统提示:
"你是企业内部知识库AI助手。请仅根据以下提供的文档内容回答用户问题。
如果文档中没有相关信息，请如实告知。回答时请引用文档来源。"

上下文:
"参考文档片段:
[1] 来源: {文档标题}, 片段: {chunk内容}
[2] 来源: {文档标题}, 片段: {chunk内容}
...

对话历史: ..."
```

---

## 十、实施阶段

### 阶段一：基础设施搭建
- 项目目录初始化
- Poetry 依赖管理初始化（pyproject.toml）
- Loguru 结构化日志配置
- FastAPI 项目骨架 + Pydantic Settings 配置管理
- MySQL 数据库表创建（Alembic迁移 + SQLAlchemy async）
- Redis 连接配置 + Celery 应用配置
- Chroma 初始化配置
- Vue 3 + Element Plus 项目脚手架搭建
- Nginx 基础配置

### 阶段二：认证与用户管理
- JWT 认证系统（登录/注册/刷新/登出）
- 用户CRUD API + Element Plus 前端页面
- 前端路由守卫（Pinia + Vue Router）

### 阶段三：文档管理
- 文档上传API + 文件存储（uploads/）
- 多格式文档解析器（PDF→PyPDF2 / Word→python-docx / MD→markdown / TXT）
- 文档分块 + 向量化 → Chroma 入库
- Celery 异步任务封装（文档处理、向量嵌入）
- 文档CRUD API + Element Plus 前端管理页面
- 文档预览功能
- 知识分类管理

### 阶段四：AI问答核心
- RAG Pipeline 完整实现
- DeepSeek LLM 接入（Chat + Embedding）
- SSE 流式响应
- 多轮对话管理
- 引用溯源功能
- 前端问答界面（对话式UI）

### 阶段五：对话历史与反馈
- 对话历史存储与查询
- 前端对话历史页面
- 点赞/点踩反馈功能

### 阶段六：集成与部署
- Nginx 配置联调
- 全链路测试
- 部署文档编写

---

## 十一、验证计划

| 验证项 | 验证方法 |
|--------|---------|
| Poetry 环境 | `poetry install` 成功，依赖版本锁定无误 |
| 用户认证 | 测试登录/注册/Token刷新/未登录拦截 |
| Celery 异步 | 上传文档后检查Celery Worker日志，确认异步处理正确执行 |
| 文档上传与入库 | 上传不同格式文档，检查MySQL元数据 + Chroma向量是否正确存入 |
| Loguru 日志 | 检查结构化日志输出，验证JSON格式正确 |
| RAG问答准确性 | 上传测试文档后提问，检查回答是否引用正确来源 |
| 多轮对话 | 连续提问3-5轮，验证上下文是否正确保持 |
| 引用溯源 | 检查AI回答中是否包含 `[来源: xxx文档]` 标记 |
| 流式响应 | 验证SSE流式输出是否正常工作 |
| 对话历史 | 创建多组对话后，检查历史列表和详情展示 |
| 反馈功能 | 测试点赞/点踩，验证数据库记录正确 |
| 文档预览 | 上传各格式文档后验证预览渲染效果 |
| Element Plus | 检查各页面UI组件正常渲染，主题一致 |
| Nginx代理 | 验证前端访问 + API代理转发是否正常 |

---

## 十二、待确认事项（后续迭代）

- [ ] 是否需要文档全文关键词搜索（基于MySQL全文索引或Elasticsearch）
- [ ] 是否需要数据看板/统计页面（问答量、热门问题、文档覆盖率等）
- [ ] 是否需要知识库定期更新/增量同步机制
- [ ] 是否需要模型切换功能（支持配置多个大模型）
- [ ] 是否需要导出对话报告
- [ ] 是否需要操作日志/审计功能
