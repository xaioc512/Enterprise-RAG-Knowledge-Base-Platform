# AI Agent 多步推理引擎 — 功能介绍与实现指南

> 适用场景：向另一个项目的 AI 介绍本系统的 Agent 架构，可作为提示词模板直接使用。

---

## 一、Agent 是什么

这是一个基于 **LangGraph** 构建的 **多步推理 AI Agent**，运行在「企业私有化生成式AI知识库平台」中。它不仅仅是简单的 RAG（检索增强生成），而是具备**自主决策能力**的智能体——能根据知识库检索结果的质量，自动判断下一步该做什么。

### 核心能力

| 能力 | 说明 |
|------|------|
| 知识库检索 | 优先从企业 Chroma 向量数据库检索相关文档 |
| 联网搜索 | 知识库无结果时，自动通过 DuckDuckGo 搜索互联网 |
| 数据分析 | 内置 Pandas 分析工具，可处理统计/趋势类问题 |
| 多步推理 | 不是一次性回答，而是经过「检索→判断→（搜索）→生成」的思考链 |
| 流式输出 | 通过 SSE 实时输出思考步骤 + 生成内容 |
| 权限感知 | 检索时自动过滤用户无权访问的文档 |

---

## 二、架构概览

```
┌──────────────────────────────────────────────────────┐
│                    用户提问                            │
└──────────────────────┬───────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────┐
│                 LangGraph Agent                       │
│                                                       │
│  ┌──────────┐    ┌──────────┐    ┌──────────────┐   │
│  │ retrieve │───▶│  judge   │───▶│  generate    │   │
│  │ (知识库)  │    │ (判断)   │    │  (生成回答)   │   │
│  └──────────┘    └────┬─────┘    └──────────────┘   │
│                       │                               │
│                       │ 知识库不足                     │
│                       ▼                               │
│                 ┌──────────────┐                      │
│                 │ web_search   │──────────────────────│
│                 │ (联网搜索)    │                      │
│                 └──────────────┘                      │
└──────────────────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────┐
│              DeepSeek Chat (流式生成)                  │
└──────────────────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────┐
│              SSE 流式响应 → 前端渲染                    │
│   {type: "thinking"} → 思考步骤显示                    │
│   {type: "token"}    → 逐字流式输出                    │
│   {type: "sources"}  → 来源引用                        │
│   {type: "done"}     → 完成事件                        │
└──────────────────────────────────────────────────────┘
```

---

## 三、文件结构

```
backend/app/rag/
├── agent.py          # ★ LangGraph Agent 核心：状态图定义、节点、路由
├── tools.py          # ★ Agent 工具集：封装成 LangChain tool 的函数
├── web_search.py     # DuckDuckGo 联网搜索实现
├── retriever.py      # Chroma 向量检索（权限过滤）
├── generator.py      # DeepSeek Chat 流式生成（OpenAI 兼容 SDK）
├── pipeline.py       # 标准 RAG Prompt 构建 & 管线编排（对比参考）
├── embedder.py       # DeepSeek Embedding 封装
├── loader.py         # 文档加载器（PDF/Word/Markdown/TXT）
└── splitter.py       # 文本分块器
```

---

## 四、核心代码解析

### 4.1 Agent 状态定义（AgentState）

```python
class AgentState(TypedDict):
    """在 LangGraph 节点间流转的状态对象"""
    question: str              # 用户原始问题
    history: list[dict]        # 对话历史 [{role, content}, ...]
    messages: list             # LangChain 消息列表（自动 add_messages 合并）
    kb_results: str            # 知识库检索结果文本
    web_results: str           # 网络搜索结果文本
    analysis: str              # 数据分析结果
    thinking_steps: list[str]  # 思考步骤日志（前端实时展示）
    final_answer: str          # 最终构建的 prompt（供 LLM 消费）
```

### 4.2 Agent 工具集（3个）

每个工具都用 `@tool` 装饰器封装，Agent 可自主决定调用哪个：

| 工具 | 函数 | 用途 |
|------|------|------|
| `search_knowledge_base` | Chroma 向量检索 Top-5 | 企业知识库搜索 |
| `search_web` | DuckDuckGo 搜索 Top-3 | 互联网补充搜索 |
| `analyze_data` | Pandas 数据分析 | 统计/趋势分析 |

```python
@tool
def search_knowledge_base(query: str) -> str:
    """在企业内部知识库中搜索相关文档内容。返回带来源标注的文本片段。"""
    results = search_similar(query, k=5)
    # ... 格式化为 [kb1] 来源: xxx\n内容: xxx
```

### 4.3 Agent 图节点（4个）

```
retrieve ──▶ judge ──▶ generate ──▶ END
                │
                └──▶ web_search ──▶ generate
```

| 节点 | 职责 | 输入 | 输出 |
|------|------|------|------|
| `retrieve_node` | 调用知识库检索 | question | kb_results |
| `judge_node` | 评估检索质量，决定路由 | kb_results | 路由决策 |
| `web_search_node` | 调用联网搜索（仅在 kb 不足时） | question | web_results |
| `generate_node` | 汇总所有上下文，构建最终 prompt | kb + web + history + question | final_answer |

### 4.4 条件路由（核心决策逻辑）

```python
def route_after_judge(state: AgentState) -> Literal["generate", "web_search"]:
    """判断知识库结果是否足够"""
    has_kb = bool(state["kb_results"]) and "未找到" not in state["kb_results"]
    if has_kb:
        return "generate"    # 知识库有结果 → 直接生成
    return "web_search"      # 知识库不足 → 联网搜索

# 添加到图中
workflow.add_conditional_edges("judge", route_after_judge, {
    "generate": "generate",
    "web_search": "web_search",
})
```

### 4.5 单例模式 & 执行入口

```python
_agent_graph = None

def get_agent() -> StateGraph:
    """全局单例，避免重复编译图"""
    global _agent_graph
    if _agent_graph is None:
        _agent_graph = build_agent_graph()
    return _agent_graph

async def run_agent(question: str, history: list[dict]) -> AgentState:
    """执行 Agent 的入口函数，返回完整状态"""
    agent = get_agent()
    initial_state = { "question": question, "history": history, ... }
    final_state = agent.invoke(initial_state)  # 同步执行整个图
    return final_state
```

---

## 五、API 集成（SSE 流式）

Agent 通过 `/api/chat/send` 端点暴露，`mode: "agent"` 启用：

```
POST /api/chat/send
{
  "conversation_id": "uuid-or-null",
  "message": "公司年假政策是什么？",
  "mode": "agent"          // ← "rag" 或 "agent"
}
```

### SSE 事件类型

| type | 含义 | 数据结构 |
|------|------|----------|
| `thinking` | Agent 思考步骤 | `{step: "检索知识库..."}` |
| `sources` | 引用来源列表 | `{sources: [{title, chunk_index, content_preview}]}` |
| `token` | LLM 生成的文本片段 | `{content: "年假"}` |
| `done` | 回答完成 | `{message_id, conversation_id}` |
| `error` | 出错 | `{message: "错误信息"}` |

### 核心处理流程

```python
if mode == "agent":
    # 1. 运行 Agent，获取状态
    agent_state = await run_agent(message, history)

    # 2. 流式输出思考步骤
    for step in agent_state["thinking_steps"]:
        yield f"data: {json.dumps({'type': 'thinking', 'step': step})}\n\n"

    # 3. 输出引用来源
    yield f"data: {json.dumps({'type': 'sources', 'sources': sources})}\n\n"

    # 4. Agent 构建的 prompt 交给 LLM 流式生成
    async for token in generate_stream(agent_prompt):
        yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"

    # 5. 完成
    yield f"data: {json.dumps({'type': 'done', ...})}\n\n"
```

---

## 六、Agent vs 标准 RAG 对比

| 维度 | 标准 RAG 模式 | Agent 模式 |
|------|--------------|-----------|
| 流程 | 检索 → 生成（固定2步） | 检索 → 判断 → (搜索) → 生成（动态） |
| 知识库无结果 | 直接告知"未找到" | 自动联网搜索补充 |
| 思考过程 | 不可见 | 前端实时展示思考步骤 |
| 工具调用 | 无 | 3个工具可自主选择 |
| 可扩展性 | 改流程需改代码 | 添加节点/工具即可扩展 |
| 适用场景 | 知识库覆盖率高 | 知识库不完整、需要联网+数据分析 |

---

## 七、技术栈

| 组件 | 技术 | 说明 |
|------|------|------|
| Agent 框架 | **LangGraph** (`langgraph`) | 状态图 + 条件路由 |
| 工具定义 | **LangChain Tools** (`@tool`) | 装饰器自动生成 schema |
| 向量检索 | **ChromaDB** 原生 API | 持久化存储，HNSW 索引 |
| Embedding | **DeepSeek Embedding** | OpenAI 兼容接口 |
| LLM 生成 | **DeepSeek Chat** (via AsyncOpenAI) | 流式输出，temperature=0.3 |
| 联网搜索 | **DuckDuckGo** (`duckduckgo_search`) | 免费、无需 API Key |
| 数据分析 | **Pandas** | Python 数据分析库 |
| Web 框架 | **FastAPI** + SSE (`StreamingResponse`) | 异步流式响应 |
| 前端 | **Vue 3** + Element Plus | EventSource 消费 SSE |

---

## 八、扩展指南

### 如何添加新工具

```python
# 1. 在 tools.py 中定义
@tool
def my_new_tool(param: str) -> str:
    """工具描述（LangGraph 会自动用于 tool choice）"""
    # ... 实现逻辑
    return result

# 2. 在 agent.py 中注册
AGENT_TOOLS = [search_knowledge_base, search_web, analyze_data, my_new_tool]
```

### 如何添加新节点

```python
# 1. 定义节点函数
def my_new_node(state: AgentState) -> AgentState:
    state["thinking_steps"].append("执行新节点...")
    # ... 逻辑
    return state

# 2. 注册到图中
workflow.add_node("my_node", my_new_node)
workflow.add_edge("some_node", "my_node")
```

### 如何扩展 AgentState

```python
class AgentState(TypedDict):
    # ... 现有字段
    my_new_field: str  # 新增字段（所有节点自动可访问）
```

---

## 九、关键设计原则

1. **有状态流转**：AgentState 贯穿所有节点，每个节点可读写任意字段
2. **条件路由**：不是硬编码流程，而是根据中间结果动态决定路径
3. **工具解耦**：每个工具是独立函数，Agent 不关心实现细节
4. **流式优先**：思考步骤和生成内容都实时推送，用户体验好
5. **单例模式**：Agent 图编译一次，全局复用（避免重复初始化）
6. **双模式共存**：Agent 和 RAG 模式共用同一 API 端点，通过 `mode` 参数切换
7. **SSE 协议**：使用标准 Server-Sent Events，前端原生 `EventSource` 即可消费
8. **权限过滤**：检索时传入 `accessible_doc_ids`，Agent 模式下由 retriever 内部处理

---

## 十、完整依赖

```toml
[tool.poetry.dependencies]
python = "^3.10"
fastapi = "^0.115"
langgraph = "^0.2"              # Agent 状态图框架
langchain = "^0.3"              # 工具装饰器、消息类型
langchain-core = "^0.3"
langchain-openai = "^0.2"       # OpenAI 兼容 SDK
chromadb = "^0.5"               # 向量数据库
openai = "^1.0"                 # AsyncOpenAI 客户端
duckduckgo-search = "^6.0"      # 免费联网搜索
pandas = "^2.0"                 # 数据分析
pydantic-settings = "^2.0"      # 配置管理
sqlalchemy = {extras = ["asyncio"], version = "^2.0"}
loguru = "^0.7"                 # 日志
```

---

## 十一、给其他项目 AI 的集成建议

如果你想在自己的项目中实现类似功能，步骤如下：

1. **安装依赖**：`langgraph` + `langchain` + `chromadb` + LLM SDK
2. **实现检索层**：向量数据库 + Embedding 模型（可用 Chroma + 任意 OpenAI 兼容 API）
3. **定义工具**：用 `@tool` 装饰器封装你的业务函数（数据库查询、API 调用、计算等）
4. **设计状态**：定义 `TypedDict` 描述 Agent 在各节点间传递的数据
5. **构建图**：`StateGraph` → `add_node` → `add_edge` / `add_conditional_edges`
6. **编译为单例**：`workflow.compile()` 一次，全局复用
7. **集成 API**：通过 FastAPI SSE 端点暴露，流式输出状态变化 + 生成内容
8. **前端消费**：`EventSource` 监听 SSE，根据 `type` 字段渲染不同 UI

---

> 关联文档：[07-AI-Pipeline设计规范](07-AI-Pipeline设计规范.md) | [05-API接口规范](05-API接口规范.md) | [02-技术选型与架构设计](02-技术选型与架构设计.md)
