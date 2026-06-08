"""RAG 查询管线 — 检索 + 生成"""

from loguru import logger

from app.rag.retriever import search_similar
from app.rag.generator import generate_stream, generate_sync

# RAG Prompt 模板
SYSTEM_PROMPT = """你是企业内部知识库AI助手。请仅根据以下提供的文档内容回答用户的问题。

规则：
1. 如果文档中包含相关信息，请准确、简洁地回答，并在回答中使用 [来源: 文档名] 标注信息来源。
2. 如果文档中不包含相关信息，请明确告知用户"知识库中暂未找到相关信息"，不要编造内容。
3. 回答使用中文，保持专业、友好的语气。"""

USER_PROMPT_TEMPLATE = """【参考文档内容】
{sources}

---
【对话历史】
{history}

---
【用户问题】
{question}

请根据以上参考文档回答问题："""


def build_prompt(
    question: str,
    sources: list[tuple[str, dict, float]],
    history: list[dict],
) -> list[dict]:
    """构建 LLM 对话消息列表"""
    # 格式化参考文档
    source_lines = []
    for i, (content, meta, score) in enumerate(sources, 1):
        title = meta.get("document_title", "未知文档")
        source_lines.append(f"[{i}] 来源: {title}\n{content}\n")
    sources_text = "\n".join(source_lines)

    # 格式化历史对话（最近10轮）
    history_lines = []
    for msg in history[-10:]:  # 最多保留5轮(10条消息)
        role = "用户" if msg["role"] == "user" else "助手"
        history_lines.append(f"{role}: {msg['content']}")
    history_text = "\n".join(history_lines) if history_lines else "（无历史对话）"

    # 构建用户 prompt
    user_content = USER_PROMPT_TEMPLATE.format(
        sources=sources_text,
        history=history_text,
        question=question,
    )

    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]


def extract_sources_from_chunks(
    chunks_with_scores: list[tuple[str, dict, float]],
) -> list[dict]:
    """从检索结果中提取来源信息"""
    seen = set()
    sources = []
    for content, meta, score in chunks_with_scores:
        title = meta.get("document_title", "未知文档")
        if title not in seen:
            seen.add(title)
            sources.append({
                "title": title,
                "chunk_index": meta.get("chunk_index", 0),
                "content_preview": content[:200],
            })
    return sources


async def rag_query(
    question: str,
    history: list[dict],
) -> tuple[str, list[dict]]:
    """
    执行 RAG 查询（流式生成）

    Yields: (token: str, sources: list | None)
    - token: LLM 生成的文本片段
    - sources: 首次 yield 时返回来源列表，后续为 None
    """
    # 1. 向量检索
    logger.info(f"RAG query: {question[:50]}...")
    results = search_similar(question)

    if not results:
        yield "知识库中暂未找到相关信息。请先上传相关文档后再提问。", []

    sources = extract_sources_from_chunks(results)

    # 2. 构建 Prompt
    messages = build_prompt(question, results, history)

    # 3. 流式生成
    async for token in generate_stream(messages):
        yield token, None  # sources 只在首次返回


async def generate_conversation_title(question: str) -> str:
    """根据首个问题生成对话标题"""
    try:
        title = await generate_sync([
            {"role": "user", "content": f"请用不超过15个字概括以下问题的主题（只返回标题文本，不要加引号）：{question}"}
        ])
        return title[:30] if title else question[:20]
    except Exception:
        return question[:20]
