"""智能问题推荐 API — /api/suggestions"""

from fastapi import APIRouter, Depends
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.conversation import Message
from app.models.document import Document
from app.middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/api/suggestions", tags=["推荐"])

# 默认推荐问题（知识库为空时展示）
FALLBACK_QUESTIONS = [
    "公司考勤迟到有什么处罚？",
    "加班补偿标准是什么？",
    "请假流程是怎样的？",
    "员工福利有哪些？",
    "如何提交报销申请？",
    "公司年假政策是什么？",
]


@router.get("/")
async def get_suggestions(
    limit: int = 6,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取推荐问题列表"""
    questions = []

    # 策略1：从最近的文档中提取问题
    result = await db.execute(
        select(Document.title)
        .where(Document.status == "done")
        .order_by(desc(Document.created_at))
        .limit(5)
    )
    recent_docs = [r[0] for r in result.all()]
    for doc_title in recent_docs:
        name = doc_title.rsplit(".", 1)[0][:30]
        questions.append(f"请介绍一下「{name}」的主要内容？")

    # 策略2：从热门提问中获取
    if len(questions) < limit:
        result = await db.execute(
            select(Message.content, func.count(Message.id).label("cnt"))
            .where(Message.role == "user")
            .group_by(Message.content)
            .order_by(desc("cnt"))
            .limit(limit)
        )
        for row in result.all():
            q = row[0][:50]
            if q not in questions:
                questions.append(q)

    # 策略3：补充默认问题
    while len(questions) < limit:
        for fq in FALLBACK_QUESTIONS:
            if fq not in questions:
                questions.append(fq)
                break
        else:
            break

    return questions[:limit]
