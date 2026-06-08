"""反馈路由 — /api/feedback"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.database import get_db
from app.models.user import User
from app.models.feedback import Feedback
from app.models.conversation import Message
from app.middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/api/feedback", tags=["反馈"])


class FeedbackRequest(BaseModel):
    message_id: str = Field(..., description="消息ID")
    rating: str = Field(..., pattern="^(like|dislike)$", description="like 或 dislike")


@router.post("/", status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    req: FeedbackRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """提交反馈"""
    # 验证消息存在
    result = await db.execute(select(Message).where(Message.id == req.message_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="消息不存在")

    # 检查是否已反馈
    result = await db.execute(
        select(Feedback).where(
            Feedback.message_id == req.message_id,
            Feedback.user_id == user.id,
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        existing.rating = req.rating
    else:
        fb = Feedback(message_id=req.message_id, user_id=user.id, rating=req.rating)
        db.add(fb)

    await db.flush()
    return {"message": "反馈已提交"}
