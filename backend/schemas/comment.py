from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from backend.schemas.user import UserResponse


class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)


class CommentResponse(BaseModel):
    id: int
    issue_id: int
    author_id: int
    content: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    author: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)
