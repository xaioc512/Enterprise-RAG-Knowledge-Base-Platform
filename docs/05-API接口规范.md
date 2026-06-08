# 05 - API接口规范

> 版本：v1.0 | 日期：2026-06-08

---

## 1. 通用规范

- Base URL: `/api`
- 认证：`Authorization: Bearer <token>`
- Content-Type: `application/json`
- 流式响应：`text/event-stream` (SSE)
- 文件上传：`multipart/form-data`

## 2. 统一响应格式

```json
// 成功
{
  "code": 200,
  "message": "success",
  "data": { ... }
}

// 分页
{
  "code": 200,
  "data": {
    "items": [...],
    "total": 100,
    "page": 1,
    "page_size": 20
  }
}

// 失败
{
  "code": 4xx,
  "message": "error description",
  "detail": null
}
```

## 3. 接口列表

### 认证 `/api/auth`
| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | /login | 登录 | 否 |
| POST | /register | 注册 | 否 |
| POST | /refresh | 刷新Token | 否 |
| POST | /logout | 登出 | 是 |

### 用户管理 `/api/users`（管理员）
| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | / | 用户列表（分页） | admin |
| POST | / | 创建用户 | admin |
| PUT | /{id} | 修改用户 | admin |
| DELETE | /{id} | 删除用户 | admin |
| GET | /me | 当前用户信息 | 是 |
| PUT | /me | 修改个人信息 | 是 |

### 知识分类 `/api/categories`
| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | / | 分类列表 | 是 |
| POST | / | 创建分类 | admin |
| PUT | /{id} | 修改分类 | admin |
| DELETE | /{id} | 删除分类 | admin |

### 文档管理 `/api/documents`
| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | / | 文档列表（筛选/分页） | 是 |
| POST | /upload | 上传文档 | admin |
| GET | /{id} | 文档详情 | 是 |
| GET | /{id}/preview | 文档预览内容 | 是 |
| DELETE | /{id} | 删除文档（含向量） | admin |
| POST | /{id}/reprocess | 重新处理 | admin |

### AI问答 `/api/chat`
| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | /send | 发送消息（SSE流式） | 是 |

**请求体**：
```json
{
  "conversation_id": "uuid or null（新建对话）",
  "message": "用户问题文本"
}
```

**SSE响应**：
```
data: {"type": "thinking", "content": ""}
data: {"type": "token", "content": "根据"}
data: {"type": "token", "content": "文档"}
...
data: {"type": "sources", "sources": [{"title": "xxx", "chunk": "..."}]}
data: {"type": "done", "message_id": "uuid"}
```

### 对话管理 `/api/conversations`
| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | / | 对话列表 | 是 |
| POST | / | 创建对话 | 是 |
| GET | /{id} | 对话详情（消息列表） | 是 |
| DELETE | /{id} | 删除对话 | 是 |
| PUT | /{id}/title | 修改标题 | 是 |

### 反馈 `/api/feedback`
| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | / | 提交反馈 | 是 |

**请求体**：
```json
{
  "message_id": "uuid",
  "rating": "like | dislike"
}
```

### 系统
| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | /api/health | 健康检查 | 否 |
| GET | /api/stats | 统计数据 | admin |

---

> 关联文档：[04-后端开发规范](04-后端开发规范.md) | [06-数据库设计规范](06-数据库设计规范.md)
