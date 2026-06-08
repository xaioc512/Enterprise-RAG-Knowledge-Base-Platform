"""AI问答路由 — /api/chat（SSE流式）"""

import json
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from loguru import logger

from app.database import async_session
from app.models.user import User
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


async def send_message(
    conversation_id: str | None,
    message: str,
    user: User,
):
    """
    核心对话逻辑 — SSE 流式输出

    修复要点：
    - 阶段1：先提交用户消息到数据库（防止流中断丢失）
    - 阶段2：RAG检索 + DeepSeek流式生成 + 保存AI回答
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

    # ========== 阶段2：RAG检索 + 流式生成 + 保存结果 ==========
    try:
        # 检索
        results = search_similar(message)
        sources = extract_sources_from_chunks(results) if results else []

        # 构建 Prompt
        messages = build_prompt(message, results, history)

        # 先发送来源
        if sources:
            yield f"data: {json.dumps({'type': 'sources', 'sources': sources}, ensure_ascii=False)}\n\n"

        # 流式生成
        full_answer = ""
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
        send_message(req.conversation_id, req.message, user),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
