"""认证 API 测试 — 注册 / 登录 / Token 验证"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.auth_service import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)
from tests.conftest import create_test_user


# ═══════════════════════════════════════════════════════════════
# 单元测试：密码哈希 / JWT
# ═══════════════════════════════════════════════════════════════

class TestPasswordHashing:
    """密码哈希与验证"""

    def test_hash_and_verify(self):
        """哈希后的密码应能验证通过"""
        password = "secure_password_123"
        hashed = hash_password(password)
        assert hashed != password
        assert verify_password(password, hashed) is True

    def test_wrong_password_fails(self):
        """错误密码应验证失败"""
        hashed = hash_password("correct_password")
        assert verify_password("wrong_password", hashed) is False

    def test_hash_is_unique(self):
        """相同密码两次哈希应产生不同结果（随机 salt）"""
        pwd = "same_password"
        h1 = hash_password(pwd)
        h2 = hash_password(pwd)
        assert h1 != h2


class TestJWT:
    """JWT Token 创建与验证"""

    def test_create_and_decode(self):
        """创建的 Token 应能被解码"""
        token = create_access_token(user_id=1, role="user", department_id=None)
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == "1"
        assert payload["role"] == "user"

    def test_token_with_department(self):
        """包含部门的 Token"""
        token = create_access_token(user_id=2, role="admin", department_id=5)
        payload = decode_access_token(token)
        assert payload["dept"] == 5

    def test_invalid_token_returns_none(self):
        """无效 Token 返回 None"""
        payload = decode_access_token("invalid.token.string")
        assert payload is None

    def test_empty_token_returns_none(self):
        """空 Token 返回 None"""
        payload = decode_access_token("")
        assert payload is None


# ═══════════════════════════════════════════════════════════════
# API 集成测试：注册 / 登录
# ═══════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    """POST /api/auth/register — 成功注册"""
    response = await client.post("/api/auth/register", json={
        "username": "newuser",
        "password": "password123",
        "email": "new@test.com",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["username"] == "newuser"
    assert data["user"]["role"] == "user"


@pytest.mark.asyncio
async def test_register_duplicate_username(client: AsyncClient):
    """POST /api/auth/register — 重复用户名"""
    # 第一次注册
    await client.post("/api/auth/register", json={
        "username": "duplicate",
        "password": "password123",
    })
    # 第二次注册（重复）
    response = await client.post("/api/auth/register", json={
        "username": "duplicate",
        "password": "another_password",
    })
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_register_short_password_fails(client: AsyncClient):
    """注册时密码过短应被拒绝"""
    response = await client.post("/api/auth/register", json={
        "username": "testuser",
        "password": "12345",  # 少于 6 字符
    })
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, db_session: AsyncSession):
    """POST /api/auth/login — 成功登录"""
    await create_test_user(db_session, "loginuser", "mypassword")
    response = await client.post("/api/auth/login", json={
        "username": "loginuser",
        "password": "mypassword",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["user"]["username"] == "loginuser"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, db_session: AsyncSession):
    """POST /api/auth/login — 错误密码"""
    await create_test_user(db_session, "user1", "correct_password")
    response = await client.post("/api/auth/login", json={
        "username": "user1",
        "password": "wrong_password",
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    """POST /api/auth/login — 不存在的用户"""
    response = await client.post("/api/auth/login", json={
        "username": "ghost_user",
        "password": "whatever",
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_endpoint_without_token(client: AsyncClient):
    """未认证请求应返回 401"""
    response = await client.get("/api/users/me")
    assert response.status_code == 401 or response.status_code == 403


@pytest.mark.asyncio
async def test_protected_endpoint_with_token(
    client: AsyncClient, db_session: AsyncSession
):
    """携带有效 Token 应返回用户信息"""
    user = await create_test_user(db_session, "authed_user")
    from tests.conftest import auth_headers
    response = await client.get("/api/users/me", headers=auth_headers(user))
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "authed_user"
