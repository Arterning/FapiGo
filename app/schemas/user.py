from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


# 用户基础模型
class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)


# 用户创建（注册）
class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=50)


# 用户更新
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    password: Optional[str] = Field(None, min_length=6, max_length=50)


# 用户响应（不包含密码）
class UserResponse(UserBase):
    id: int
    avatar_url: Optional[str] = None
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Token 相关
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None


# 用户资料更新相关
class UpdateUsernameRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)


class UpdatePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6, max_length=50)
