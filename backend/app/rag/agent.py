"""AI Agent — 基于 LangGraph 的多步推理引擎

流程:
  start → retrieve(kb) → judge → [generate] 或 [web_search] 或 [clarify]
                                            ↓
                                        generate → end
"""

from typing import TypedDict, Annotated, Literal
import json

from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from loguru import logger

from app.config import settings
from app.rag.tools import search_knowledge_base, search_web, analyze_data
from app.rag.generator import get_client

# Agent 可用的工具列表
AGENT_TOOLS = [search_knowledge_base, search_web, analyze_data]

# Agent 系统提示
AGENT_SYSTEM_PROMPT = """你是一个企业AI知识库助手，具备多步推理能力。

你可以使用以下工具：
1. search_knowledge_base(query) — 搜索企业内部知识库
2. search_web(query) — 互联网搜索（知识库无结果时使用）
3. analyze_data(question) — 数据分析（Pandas）

工作流程：
1. 首先尝试从知识库检索相关信息
2. 如果知识库有足够信息，直接回答（标注来源）
3. 如果知识库信息不足，可以联网搜索补充
4. 如果用户意图不明确，反问澄清
5. 综合所有信息给出最终回答

回答要求：
- 优先使用知识库内容，标注 [来源: 文档名]
- 网络搜索结果标注 [来源: 网络搜索]
- 如果知识库和网络都没有答案，如实告知
- 保持专业、简洁"""


class AgentState(TypedDict):
    """Agent 状态 — 在节点间流转"""
    question: str
    history: list[dict]
    messages: Annotated[list, add_messages]
    kb_results: str
    web_results: str
    analysis: str
    thinking_steps: list[str]
    final_answer: str


# === Agent 节点 ===

def retrieve_node(state: AgentState) -> AgentState:
    """从知识库检索"""
    state["thinking_steps"].append("检索知识库...")
    results = search_knowledge_base.invoke({"query": state["question"]})
    state["kb_results"] = str(results)
    return state


def judge_node(state: AgentState) -> AgentState:
    """
    判断节点：评估知识库结果是否足够回答问题。
    返回 "generate" / "web_search" / "clarify"
    """
    state["thinking_steps"].append("判断信息是否充足...")

    # 简单策略：如果知识库有结果，直接生成
    has_kb = bool(state["kb_results"]) and "未找到" not in state["kb_results"]
    if has_kb:
        state["thinking_steps"].append("知识库有相关内容，直接回答")
    else:
        state["thinking_steps"].append("知识库信息不足，尝试联网搜索")
    return state


def web_search_node(state: AgentState) -> AgentState:
    """联网搜索"""
    state["thinking_steps"].append("联网搜索中...")
    results = search_web.invoke({"query": state["question"]})
    state["web_results"] = str(results)
    return state


def generate_node(state: AgentState) -> AgentState:
    """
    综合所有上下文生成最终回答。
    这个节点在实际使用中通过 SSE 流式输出，这里返回完整内容。
    """
    state["thinking_steps"].append("生成回答...")

    # 构建上下文
    context_parts = []
    if state["kb_results"] and "未找到" not in state["kb_results"]:
        context_parts.append(f"【知识库检索结果】\n{state['kb_results']}")
    if state["web_results"] and "无网络搜索结果" not in state["web_results"]:
        context_parts.append(f"【网络搜索结果】\n{state['web_results']}")

    context = "\n\n".join(context_parts)
    if not context:
        context = "（未找到相关信息）"

    # 构建历史
    history_text = "\n".join(
        f"{'用户' if m['role'] == 'user' else '助手'}: {m['content']}"
        for m in state["history"][-6:]
    ) if state["history"] else "（无历史）"

    user_prompt = f"""【参考信息】
{context}

【对话历史】
{history_text}

【用户问题】
{state['question']}

请根据以上信息回答问题。标注信息来源。"""

    state["final_answer"] = user_prompt  # 实际的 LLM 调用在 chat.py 中完成
    return state


# === 条件路由 ===

def route_after_judge(state: AgentState) -> Literal["generate", "web_search"]:
    """根据知识库结果路由到下一个节点"""
    has_kb = bool(state["kb_results"]) and "未找到" not in state["kb_results"]
    if has_kb:
        return "generate"
    return "web_search"


# === 构建 Agent Graph ===

def build_agent_graph() -> StateGraph:
    """构建并编译 LangGraph Agent"""
    workflow = StateGraph(AgentState)

    # 添加节点
    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("judge", judge_node)
    workflow.add_node("web_search", web_search_node)
    workflow.add_node("generate", generate_node)

    # 设置边
    workflow.set_entry_point("retrieve")
    workflow.add_edge("retrieve", "judge")
    workflow.add_conditional_edges("judge", route_after_judge, {
        "generate": "generate",
        "web_search": "web_search",
    })
    workflow.add_edge("web_search", "generate")
    workflow.add_edge("generate", END)

    return workflow.compile()


# 全局单例
_agent_graph = None


def get_agent() -> StateGraph:
    """获取 Agent 实例（单例）"""
    global _agent_graph
    if _agent_graph is None:
        _agent_graph = build_agent_graph()
    return _agent_graph


async def run_agent(question: str, history: list[dict]) -> AgentState:
    """
    执行 Agent，返回最终状态。

    返回的 AgentState 包含：
    - thinking_steps: 思考步骤列表
    - kb_results / web_results: 检索结果
    - final_answer: 最终 prompt（需通过 LLM 生成最终回答）
    """
    agent = get_agent()

    initial_state: AgentState = {
        "question": question,
        "history": history,
        "messages": [HumanMessage(content=question)],
        "kb_results": "",
        "web_results": "",
        "analysis": "",
        "thinking_steps": [],
        "final_answer": "",
    }

    logger.info(f"Agent starting: {question[:50]}...")
    final_state = agent.invoke(initial_state)
    logger.info(f"Agent steps: {' → '.join(final_state['thinking_steps'])}")

    return final_state
