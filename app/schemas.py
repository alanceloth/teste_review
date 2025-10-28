from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


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

    # Pydantic v2: enable ORM mode replacement
    model_config = ConfigDict(from_attributes=True)

