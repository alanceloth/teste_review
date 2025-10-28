from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ==== Users ====

class UserCreate(BaseModel):
    """Schema para criação de usuário."""

    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)


class UserLogin(BaseModel):
    """Schema para login de usuário (JSON)."""

    username: str
    password: str


class UserResponse(BaseModel):
    """Schema de resposta de usuário (sem senha)."""

    id: int
    username: str
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """Schema de token JWT retornado no login."""

    access_token: str
    token_type: str


# ==== Tasks ====

class TaskCreate(BaseModel):
    """Schema for creating a new task."""

    title: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class TaskUpdate(BaseModel):
    """Schema for updating an existing task (all fields optional)."""

    title: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    completed: Optional[bool] = None


class TaskResponse(BaseModel):
    """Response schema for task resources."""

    id: int
    title: str
    description: Optional[str] = None
    completed: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
