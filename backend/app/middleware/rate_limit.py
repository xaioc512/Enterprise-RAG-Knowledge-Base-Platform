"""轻量级速率限制器

基于内存的滑动窗口速率限制，避免额外依赖。
生产环境可替换为 Redis 后端。
"""

import time
import threading
from collections import defaultdict
from typing import Callable

from fastapi import HTTPException, Request, status
from app.config import settings


class RateLimiter:
    """线程安全的滑动窗口速率限制器"""

    def __init__(self, max_requests: int = 200, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._store: dict[str, list[float]] = defaultdict(list)
        self._lock = threading.Lock()

    def _clean_window(self, key: str, now: float) -> list[float]:
        """清理窗口外的旧记录"""
        cutoff = now - self.window_seconds
        self._store[key] = [t for t in self._store[key] if t > cutoff]
        return self._store[key]

    def is_allowed(self, key: str) -> bool:
        """检查请求是否在限制内，如允许则记录"""
        now = time.time()
        with self._lock:
            window = self._clean_window(key, now)
            if len(window) >= self.max_requests:
                return False
            self._store[key].append(now)
            return True

    def remaining(self, key: str) -> int:
        """剩余可用请求数"""
        now = time.time()
        with self._lock:
            window = self._clean_window(key, now)
            return max(0, self.max_requests - len(window))


# 全局单例
_limiter = RateLimiter(max_requests=200, window_seconds=60)


def get_client_key(request: Request) -> str:
    """获取客户端标识符（IP 或 X-Forwarded-For）"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def rate_limit(action: str, max_requests: int = 10, window_seconds: int = 60) -> Callable:
    """FastAPI 依赖注入：返回速率限制检查函数"""

    async def check_rate_limit(request: Request) -> bool:
        client_ip = get_client_key(request)
        key = f"{client_ip}:{action}"

        # 创建临时限制器（key 粒度的精确控制）
        if not hasattr(request.app.state, "_rate_limiters"):
            request.app.state._rate_limiters = {}
        limiters = request.app.state._rate_limiters
        if key not in limiters:
            limiters[key] = RateLimiter(
                max_requests=max_requests, window_seconds=window_seconds
            )

        if not limiters[key].is_allowed(key):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"请求过于频繁，{action} 操作限制 {max_requests} 次/{window_seconds}秒",
            )
        return True

    return check_rate_limit
