"""测试配置与 Fixtures

通过 DATABASE_URL 环境变量覆盖为 SQLite 内存数据库，
无需 Monkey-patch — config.py 已支持环境变量覆盖。
"""

import os
import asyncio
from typing import AsyncGenerator

# ── 在导入任何 app 模块前设置环境变量 ─────────────────────────
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["DB_POOL_SIZE"] = "0"
os.environ["DB_MAX_OVERFLOW"] = "0"
os.environ["DB_ECHO"] = "false"
os.environ["JWT_SECRET"] = "test-secret-key-for-pytest"
os.environ["ADMIN_REGISTRATION_KEY"] = "test-admin-key"
os.environ["CHROMA_PERSIST_DIR"] = "/tmp/chroma_test"
os.environ["UPLOAD_DIR"] = "/tmp/uploads_test"
os.environ["DEEPSEEK_API_KEY"] = "sk-test-key"

import pytest
from sqlalchemy import event
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool
from httpx import AsyncClient, ASGITransport

# 现在安全导入 app — engine 将使用 SQLite
from app.main import app
from app.database import Base, get_db  # noqa: E402
from app.services.auth_service import create_access_token, hash_password  # noqa: E402
from app.models.user import User  # noqa: E402

# ── SQLite 测试引擎 ──────────────────────────────────────────
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@event.listens_for(test_engine.sync_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    """测试数据库会话（覆盖 FastAPI 依赖注入）"""
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ── Fixtures ────────────────────────────────────────────────

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
async def setup_database():
    """每个测试前重新创建数据库表"""
    import app.models  # noqa: F401
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """FastAPI 异步测试客户端"""
    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """独立数据库会话"""
    async with TestSessionLocal() as session:
        yield session


# ── 辅助函数 ────────────────────────────────────────────────

async def create_test_user(
    db: AsyncSession,
    username: str = "testuser",
    password: str = "test123456",
    role: str = "user",
    department_id: int | None = None,
) -> User:
    """在测试数据库中创建用户"""
    user = User(
        username=username,
        password_hash=hash_password(password),
        email=f"{username}@test.com",
        role=role,
        department_id=department_id,
        is_active=True,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


def auth_headers(user: User) -> dict:
    """生成认证请求头"""
    token = create_access_token(user.id, user.role, user.department_id)
    return {"Authorization": f"Bearer {token}"}
