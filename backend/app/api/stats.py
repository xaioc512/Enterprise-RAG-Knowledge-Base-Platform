"""数据统计 API — /api/stats（管理员）"""

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, text, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.document import Document
from app.models.conversation import Message, Conversation
from app.models.feedback import Feedback
from app.middleware.auth_middleware import get_current_admin

router = APIRouter(prefix="/api/stats", tags=["数据统计"])


@router.get("/overview")
async def get_overview(
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """概览数据"""
    # 文档总数
    r = await db.execute(select(func.count(Document.id)))
    total_docs = r.scalar()

    # 今日上传
    today = datetime.now().strftime("%Y-%m-%d")
    r = await db.execute(
        select(func.count(Document.id)).where(func.date(Document.created_at) == today)
    )
    today_docs = r.scalar()

    # 用户总数
    r = await db.execute(select(func.count(User.id)))
    total_users = r.scalar()

    # 总提问数
    r = await db.execute(
        select(func.count(Message.id)).where(Message.role == "user")
    )
    total_questions = r.scalar()

    # 今日提问
    r = await db.execute(
        select(func.count(Message.id)).where(
            Message.role == "user", func.date(Message.created_at) == today
        )
    )
    today_questions = r.scalar()

    # 对话总数
    r = await db.execute(select(func.count(Conversation.id)))
    total_convs = r.scalar()

    return {
        "documents": total_docs,
        "today_documents": today_docs,
        "users": total_users,
        "questions": total_questions,
        "today_questions": today_questions,
        "conversations": total_convs,
    }


@router.get("/trends")
async def get_trends(
    days: int = Query(7, ge=1, le=90),
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """近N天提问趋势"""
    results = []
    for i in range(days - 1, -1, -1):
        date_str = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        r = await db.execute(
            select(func.count(Message.id)).where(
                Message.role == "user",
                func.date(Message.created_at) == date_str,
            )
        )
        results.append({"date": date_str, "count": r.scalar()})
    return results


@router.get("/feedback")
async def get_feedback(
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """反馈统计"""
    r = await db.execute(
        select(Feedback.rating, func.count(Feedback.id)).group_by(Feedback.rating)
    )
    rows = r.all()
    result = {"like": 0, "dislike": 0}
    for rating, count in rows:
        result[rating] = count
    return result
