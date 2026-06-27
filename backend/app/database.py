"""数据库连接管理 — SQLAlchemy 2.0 async"""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

_engine_kwargs: dict = {
    "echo": settings.DB_ECHO or settings.DEBUG,
    "pool_pre_ping": True,
}
if settings.DB_POOL_SIZE > 0:
    _engine_kwargs["pool_size"] = settings.DB_POOL_SIZE
if settings.DB_MAX_OVERFLOW > 0:
    _engine_kwargs["max_overflow"] = settings.DB_MAX_OVERFLOW

engine = create_async_engine(settings.ASYNC_DATABASE_URL, **_engine_kwargs)

async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """SQLAlchemy 声明式基类"""
    pass


async def get_db() -> AsyncSession:
    """FastAPI 依赖注入：获取数据库会话"""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def check_db_connection() -> bool:
    """健康检查：测试数据库连接"""
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        from app.utils.logger import logger
        logger.warning(f"Database connection check failed: {e}")
        return False
