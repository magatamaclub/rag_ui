from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from .models import UserRole, DifyAppType


class UserBase(BaseModel):
    username: str
    email: str


class UserCreate(UserBase):
    password: str
    role: Optional[UserRole] = UserRole.USER


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(UserBase):
    id: int
    role: UserRole
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class DifyAppBase(BaseModel):
    name: str
    app_type: DifyAppType
    api_key: str
    api_url: str
    description: Optional[str] = None


class DifyAppCreate(DifyAppBase):
    pass


class DifyAppUpdate(BaseModel):
    name: Optional[str] = None
    app_type: Optional[DifyAppType] = None
    api_key: Optional[str] = None
    api_url: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class DifyAppResponse(DifyAppBase):
    id: int
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
