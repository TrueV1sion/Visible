from typing import Optional
from pydantic import BaseModel, EmailStr, validator
from datetime import datetime
from ..models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    role: Optional[UserRole] = UserRole.VIEWER
    is_active: Optional[bool] = True


class UserCreate(UserBase):
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        from ..core.security import validate_password
        if not validate_password(v):
            raise ValueError(
                'Password must be at least 8 characters with uppercase, lowercase, number, and special character'
            )
        return v


class UserUpdate(UserBase):
    password: Optional[str] = None
    
    @validator('password')
    def validate_password(cls, v):
        if v is not None:
            from ..core.security import validate_password
            if not validate_password(v):
                raise ValueError(
                    'Password must be at least 8 characters with uppercase, lowercase, number, and special character'
                )
        return v


class User(UserBase):
    id: int
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int


class TokenRefresh(BaseModel):
    refresh_token: str


class TokenPayload(BaseModel):
    sub: int
    exp: int
    type: str