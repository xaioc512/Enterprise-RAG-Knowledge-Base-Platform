"""认证路由 — /api/auth"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings

from app.database import get_db
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserInfo,
)
from app.services.auth_service import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)
from app.middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    """用户登录"""
    result = await db.execute(
        select(User).where(User.username == req.username)
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号已被禁用",
        )

    access_token = create_access_token(user.id, user.role, user.department_id)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserInfo(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
            department_id=user.department_id,
        ),
    )


@router.post("/register", response_model=TokenResponse)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """用户注册 — 提供正确的 admin_key 则注册为管理员"""
    # 检查用户名是否已存在
    result = await db.execute(
        select(User).where(User.username == req.username)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="用户名已存在",
        )

    # 检查邮箱是否已存在
    if req.email:
        result = await db.execute(
            select(User).where(User.email == req.email)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="邮箱已被使用",
            )

    # 判断角色：提供正确管理员密钥 → admin，否则 → user
    role = "user"
    if req.admin_key and settings.ADMIN_REGISTRATION_KEY and req.admin_key == settings.ADMIN_REGISTRATION_KEY:
        role = "admin"

    user = User(
        username=req.username,
        password_hash=hash_password(req.password),
        email=req.email,
        role=role,
        department_id=req.department_id if role == "user" else None,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    access_token = create_access_token(user.id, user.role, user.department_id)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserInfo(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
            department_id=user.department_id,
        ),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    user: User = Depends(get_current_user),
):
    """刷新 Token"""
    access_token = create_access_token(user.id, user.role, user.department_id)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserInfo(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
            department_id=user.department_id,
        ),
    )


@router.post("/logout")
async def logout(user: User = Depends(get_current_user)):
    """登出（客户端应清除 Token）"""
    return {"message": "已登出"}
