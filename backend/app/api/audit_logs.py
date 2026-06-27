"""审计日志查询 API — /api/audit-logs（管理员）"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.audit_log import AuditLog
from app.middleware.auth_middleware import get_current_admin

router = APIRouter(prefix="/api/audit-logs", tags=["审计日志"])


@router.get("/")
async def list_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: int | None = None,
    action: str | None = None,
    days: int = Query(7, ge=1, le=90),
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """审计日志列表"""
    query = select(AuditLog)
    count_query = select(func.count(AuditLog.id))

    # 时间过滤
    from datetime import datetime, timedelta
    since = datetime.now() - timedelta(days=days)
    query = query.where(AuditLog.created_at >= since)
    count_query = count_query.where(AuditLog.created_at >= since)

    if user_id:
        query = query.where(AuditLog.user_id == user_id)
        count_query = count_query.where(AuditLog.user_id == user_id)
    if action:
        query = query.where(AuditLog.action == action)
        count_query = count_query.where(AuditLog.action == action)

    r = await db.execute(count_query)
    total = r.scalar()

    r = await db.execute(
        query.order_by(desc(AuditLog.created_at))
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    logs = r.scalars().all()

    return {
        "items": [
            {
                "id": l.id, "user_id": l.user_id, "username": l.username,
                "action": l.action, "resource_type": l.resource_type,
                "resource_id": l.resource_id, "detail": l.detail,
                "created_at": l.created_at.isoformat(),
            }
            for l in logs
        ],
        "total": total, "page": page, "page_size": page_size,
    }
