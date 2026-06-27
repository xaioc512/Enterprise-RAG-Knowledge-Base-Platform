"""AI问答路由 — /api/chat（SSE流式）"""

import json
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import select, or_
from loguru import logger

from app.database import async_session
from app.models.user import User
from app.models.document import Document, DocDepartment
from app.middleware.auth_middleware import get_current_user
from app.rag.pipeline import build_prompt, extract_sources_from_chunks, generate_conversation_title
from app.rag.retriever import search_similar
from app.rag.generator import generate_stream
from app.services.chat_service import (
    get_or_create_conversation,
    save_message,
    get_history,
    update_conversation_title,
)

router = APIRouter(prefix="/api/chat", tags=["AI问答"])


class SendMessageRequest(BaseModel):
    conversation_id: str | None = Field(None, description="对话ID，为空则创建新对话")
    message: str = Field(..., min_length=1, max_length=5000, description="用户问题")
    mode: str = Field("rag", description="模式: rag(默认) 或 agent(AI Agent多步推理)")


async def _get_accessible_doc_ids(user: User) -> set[int] | None:
    """获取用户有权访问的文档ID集合。Admin返回None（不限制）。"""
    if user.role == "admin":
        return None

    conditions = [Document.visibility == "public"]
    if user.department_id:
        conditions.append(
            (Document.visibility == "department") & (Document.department_id == user.department_id)
        )
        shared_subq = (
            select(DocDepartment.document_id)
            .where(DocDepartment.department_id == user.department_id)
        )
        conditions.append(Document.id.in_(shared_subq))

    async with async_session() as db:
        result = await db.execute(
            select(Document.id).where(or_(*conditions))
        )
        return set(row[0] for row in result.all())


async def send_message(
    conversation_id: str | None,
    message: str,
    user: User,
    mode: str = "rag",
):
    """
    核心对话逻辑 — SSE 流式输出

    mode: "rag" (标准RAG检索) / "agent" (LangGraph多步推理Agent)
    """
    # ========== 阶段1：保存用户消息并立即提交 ==========
    async with async_session() as db1:
        try:
            conv = await get_or_create_conversation(conversation_id, user, db1)
            await save_message(conv, "user", message, db=db1)
            history = await get_history(conv.id, db1)
            await db1.commit()
        except Exception as e:
            await db1.rollback()
            logger.error(f"Chat phase1 error: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"
            return

    # ========== 阶段2：RAG检索 或 Agent推理 + 流式生成 + 保存结果 ==========
    try:
        full_answer = ""
        sources = []

        if mode == "agent":
            # === Agent 模式：LangGraph 多步推理 ===
            from app.rag.agent import run_agent

            # 运行 Agent，流式输出思考步骤
            agent_state = await run_agent(message, history)

            # 输出思考步骤
            for step in agent_state["thinking_steps"]:
                yield f"data: {json.dumps({'type': 'thinking', 'step': step}, ensure_ascii=False)}\n\n"

            # 提取来源
            if agent_state["kb_results"] and "未找到" not in agent_state["kb_results"]:
                sources = extract_sources_from_chunks(
                    search_similar(message)
                ) if search_similar(message) else []
                if sources:
                    yield f"data: {json.dumps({'type': 'sources', 'sources': sources}, ensure_ascii=False)}\n\n"

            # 使用 Agent 构建的 prompt 生成最终回答
            agent_prompt = [
                {"role": "system", "content": "你是企业AI知识库助手。请基于提供的参考信息回答问题，标注信息来源。"},
                {"role": "user", "content": agent_state["final_answer"]},
            ]
            async for token in generate_stream(agent_prompt):
                full_answer += token
                yield f"data: {json.dumps({'type': 'token', 'content': token}, ensure_ascii=False)}\n\n"

        else:
            # === RAG 模式：标准检索+生成 ===
            accessible_ids = await _get_accessible_doc_ids(user)
            results = search_similar(message, accessible_doc_ids=accessible_ids)
            sources = extract_sources_from_chunks(results) if results else []
            messages = build_prompt(message, results, history)

            if sources:
                yield f"data: {json.dumps({'type': 'sources', 'sources': sources}, ensure_ascii=False)}\n\n"

            async for token in generate_stream(messages):
                full_answer += token
                yield f"data: {json.dumps({'type': 'token', 'content': token}, ensure_ascii=False)}\n\n"

        # 保存AI回答 + 更新标题
        async with async_session() as db2:
            try:
                conv = await get_or_create_conversation(conv.id, user, db2)
                assistant_msg = await save_message(
                    conv, "assistant", full_answer,
                    sources=sources, db=db2,
                )
                # 更新标题（如果是新对话）
                if not conversation_id and len([m for m in history if m["role"] == "user"]) <= 1:
                    try:
                        title = await generate_conversation_title(message)
                        conv.title = title[:30]
                    except Exception:
                        conv.title = message[:20]
                await db2.commit()

                # 发送完成事件
                yield f"data: {json.dumps({'type': 'done', 'message_id': assistant_msg.id, 'conversation_id': conv.id}, ensure_ascii=False)}\n\n"

            except Exception as e:
                await db2.rollback()
                logger.error(f"Chat phase2 save error: {e}")
                yield f"data: {json.dumps({'type': 'error', 'message': f'保存失败: {str(e)}'}, ensure_ascii=False)}\n\n"

    except Exception as e:
        logger.error(f"Chat phase2 error: {e}")
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"


@router.post("/send")
async def chat_send(
    req: SendMessageRequest,
    user: User = Depends(get_current_user),
):
    """发送消息，返回 SSE 流式响应"""
    return StreamingResponse(
        send_message(req.conversation_id, req.message, user, mode=req.mode),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
