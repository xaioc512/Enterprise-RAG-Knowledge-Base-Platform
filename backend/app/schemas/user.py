"""用户管理 Pydantic 模型"""

from datetime import datetime
from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=6, max_length=128)
    email: str | None = Field(None, max_length=100)
    role: str = Field("user", pattern="^(admin|user)$")
    department_id: int | None = None


class UserUpdate(BaseModel):
    email: str | None = Field(None, max_length=100)
    role: str | None = Field(None, pattern="^(admin|user)$")
    department_id: int | None = None
    is_active: bool | None = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: str | None
    role: str
    department_id: int | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    items: list[UserResponse]
    total: int
    page: int
    page_size: int
