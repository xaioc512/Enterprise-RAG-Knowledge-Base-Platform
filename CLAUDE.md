# CLAUDE.md — 企业私有化生成式AI平台

## 项目概述

企业私有化生成式AI知识问答平台，基于RAG技术，Vue3 + FastAPI + LangChain + DeepSeek。

---

## 标准文档路径

| 文档 | 路径 | 用途 |
|------|------|------|
| 需求规格 | `企业私有化生成式AI平台_需求规格与实施计划.md` | 项目总览 |
| 开发需求 | `docs/01-开发需求规格.md` | 功能需求详情 |
| 技术架构 | `docs/02-技术选型与架构设计.md` | 技术选型与架构 |
| **前端设计规范** | `docs/03-前端设计规范.md` | **前端开发强制执行规范** |
| 后端开发规范 | `docs/04-后端开发规范.md` | 后端代码规范 |
| API规范 | `docs/05-API接口规范.md` | 接口定义 |
| 数据库设计 | `docs/06-数据库设计规范.md` | 表结构与存储设计 |
| AI Pipeline | `docs/07-AI-Pipeline设计规范.md` | RAG模块设计 |
| **执行步骤** | `docs/08-开发执行步骤.md` | **当前执行进度** |
| 前端Skill | `skill.md` | Anthropic frontend-design skill |
| 开发日志 | `devlog/YYYY-MM-DD.md` | 每日开发记录 |

---

## 工作说明

### 开始工作前
1. 阅读 `devlog/` 中最新日期的开发日志，了解当前进度
2. 阅读 `docs/08-开发执行步骤.md`，确认下一步任务
3. 涉及前端开发时，**必须先阅读** `docs/03-前端设计规范.md` 和 `skill.md`

### 开发过程中
1. **小步迭代**：每完成一个子步骤，立即验证运行
2. **零Bug**：编译错误/运行时错误立即修复，不累积
3. 修改代码前，先阅读相关规范文档
4. 涉及数据库变更，先检查 `docs/06-数据库设计规范.md`
5. 涉及API变更，先检查 `docs/05-API接口规范.md`

### 每日结束时
1. 更新 `devlog/YYYY-MM-DD.md`，记录完成事项和待办事项
2. 更新 `docs/08-开发执行步骤.md` 中的勾选状态
3. 如有新的设计决策，更新对应的规范文档

---

## 关键约束

- **前端设计**：禁止使用Inter/Roboto/Arial等通用字体，禁止紫色渐变+白色背景等AI套路审美
- **后端分层**：api → services → models，api层仅做参数校验和响应
- **异步优先**：数据库操作全部async，长任务走Celery
- **配置**：所有环境相关配置通过.env注入，使用pydantic-settings
- **安全**：密码bcrypt哈希，JWT鉴权，SQL注入防护（ORM参数绑定）

## 技术栈速查

- Python 3.10+, Poetry, FastAPI, SQLAlchemy 2.0 async, Alembic, Celery, Loguru
- Vue 3, Element Plus, Pinia, Vue Router, Axios
- MySQL 8.0, Redis, Chroma
- LangChain, LangGraph, DeepSeek API
- Nginx
