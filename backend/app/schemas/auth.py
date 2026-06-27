"""认证相关 Pydantic 模型"""

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=6, max_length=128)


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=6, max_length=128)
    email: str | None = Field(None, max_length=100)
    admin_key: str | None = Field(None, description="管理员注册密钥，正确则注册为管理员")
    department_id: int | None = Field(None, description="所属部门ID")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserInfo"


class UserInfo(BaseModel):
    id: int
    username: str
    email: str | None
    role: str
    department_id: int | None = None

    model_config = {"from_attributes": True}


class RefreshRequest(BaseModel):
    pass  # Token 从 Authorization header 中获取
