"""
User Schemas
============
Pydantic models for user registration, login, and response serialization.
Includes custom validators for password strength and role values.
"""

from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    email: EmailStr
    username: str = ""
    password: str = ""
    role: Optional[str] = "customer"

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v):
        """Password must be at least 6 characters."""
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters long")
        return v

    @field_validator("username")
    @classmethod
    def username_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Username cannot be empty")
        return v.strip()

    @field_validator("role")
    @classmethod
    def valid_role(cls, v):
        allowed = {"admin", "customer"}
        if v not in allowed:
            raise ValueError(f"Role must be one of: {allowed}")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    role: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[int] = None
