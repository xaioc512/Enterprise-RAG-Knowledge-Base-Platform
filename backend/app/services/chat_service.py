"""对话管理服务"""

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Conversation, Message
from app.models.user import User
from app.rag.pipeline import generate_conversation_title


async def get_or_create_conversation(
    conversation_id: str | None,
    user: User,
    db: AsyncSession,
) -> Conversation:
    """获取已有对话或创建新对话"""
    if conversation_id:
        result = await db.execute(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user.id,
            )
        )
        conv = result.scalar_one_or_none()
        if conv:
            return conv

    conv = Conversation(user_id=user.id, title="新对话")
    db.add(conv)
    await db.flush()
    await db.refresh(conv)
    return conv


async def save_message(
    conversation: Conversation,
    role: str,
    content: str,
    sources: list[dict] | None = None,
    db: AsyncSession | None = None,
) -> Message:
    """保存消息到数据库"""
    msg = Message(
        conversation_id=conversation.id,
        role=role,
        content=content,
        sources=sources,
    )
    db.add(msg)
    await db.flush()
    await db.refresh(msg)
    return msg


async def get_history(conversation_id: str, db: AsyncSession) -> list[dict]:
    """获取对话历史（最近消息）"""
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    )
    messages = result.scalars().all()
    return [
        {"role": m.role, "content": m.content}
        for m in messages
    ]


async def update_conversation_title(
    conversation: Conversation,
    question: str,
    db: AsyncSession,
) -> None:
    """如果是首条消息，用 DeepSeek 生成对话标题"""
    # 检查消息数量
    result = await db.execute(
        select(func.count(Message.id)).where(
            Message.conversation_id == conversation.id
        )
    )
    count = result.scalar()
    if count <= 1:  # 刚保存了用户消息，count=1
        title = await generate_conversation_title(question)
        conversation.title = title
        await db.flush()
