"""审计日志中间件 — 自动记录 API 操作"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger

# 需要记录的操作类型映射
METHOD_ACTION_MAP = {
    "POST": "CREATE",
    "PUT": "UPDATE",
    "DELETE": "DELETE",
    "GET": "QUERY",
}

# 路径到资源类型的映射
def get_resource_type(path: str) -> str:
    if path.startswith("/api/auth"):
        return "auth"
    if path.startswith("/api/users"):
        return "user"
    if path.startswith("/api/documents"):
        return "document"
    if path.startswith("/api/categories"):
        return "category"
    if path.startswith("/api/conversations"):
        return "conversation"
    if path.startswith("/api/chat"):
        return "chat"
    if path.startswith("/api/feedback"):
        return "feedback"
    if path.startswith("/api/departments"):
        return "department"
    return "other"


class AuditMiddleware(BaseHTTPMiddleware):
    """审计中间件 — 记录所有 API 请求到数据库"""

    async def dispatch(self, request: Request, call_next):
        # 跳过健康检查
        if request.url.path == "/api/health":
            return await call_next(request)

        # 记录请求开始
        start_time = __import__("time").time()
        response = await call_next(request)
        duration = __import__("time").time() - start_time

        # 仅记录写操作（POST/PUT/DELETE）+ 登录操作
        action = METHOD_ACTION_MAP.get(request.method)
        if action and response.status_code < 400:
            try:
                # 获取用户信息（从 JWT token）
                token = request.headers.get("Authorization", "").replace("Bearer ", "")
                username = "anonymous"
                user_id = None

                if token:
                    from app.services.auth_service import decode_access_token
                    payload = decode_access_token(token)
                    if payload:
                        user_id = int(payload.get("sub", "0"))
                        # 从缓存或简单查询获取用户名
                        username = f"user_{user_id}"

                # 提取资源 ID
                path_parts = request.url.path.rstrip("/").split("/")
                resource_id = None
                if len(path_parts) >= 3 and path_parts[-1].isdigit():
                    resource_id = path_parts[-1]
                elif len(path_parts) >= 3 and len(path_parts) >= 3:
                    resource_id = path_parts[-1] if "-" in path_parts[-1] else None

                from app.database import async_session
                from app.models.audit_log import AuditLog

                async with async_session() as db:
                    log_entry = AuditLog(
                        user_id=user_id,
                        username=username,
                        action=action,
                        resource_type=get_resource_type(request.url.path),
                        resource_id=resource_id,
                        ip_address=request.client.host if request.client else None,
                        user_agent=request.headers.get("user-agent", "")[:500],
                        detail={
                            "method": request.method,
                            "path": request.url.path,
                            "status": response.status_code,
                            "duration_ms": round(duration * 1000, 2),
                        },
                    )
                    db.add(log_entry)
                    await db.commit()
            except Exception as e:
                logger.warning(f"Audit log error: {e}")

        return response
