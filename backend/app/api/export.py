"""对话导出 API — /api/export"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import PlainTextResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.database import get_db
from app.models.user import User
from app.models.conversation import Conversation, Message
from app.middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/api/export", tags=["导出"])


@router.get("/conversation/{conversation_id}")
async def export_conversation(
    conversation_id: str,
    format: str = Query("md", regex="^(md)$"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """导出对话为 Markdown 格式"""
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user.id,
        )
    )
    conv = result.scalar_one_or_none()
    if not conv:
        raise HTTPException(404, "对话不存在")

    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    )
    messages = result.scalars().all()

    # 生成 Markdown
    lines = [
        f"# {conv.title}",
        f"",
        f"> 导出时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"> 消息数：{len(messages)}",
        f"",
        "---",
        "",
    ]

    for m in messages:
        role_label = "**用户**" if m.role == "user" else "**AI 助手**"
        lines.append(f"### {role_label}")
        lines.append("")
        lines.append(m.content)
        if m.sources:
            lines.append("")
            lines.append("> 参考来源：")
            for src in m.sources:
                lines.append(f"> - {src.get('title', '未知文档')}")
        lines.append("")
        lines.append("---")
        lines.append("")

    content = "\n".join(lines)
    filename = f"{conv.title}_{datetime.now().strftime('%Y%m%d')}.md"

    return PlainTextResponse(
        content=content,
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
