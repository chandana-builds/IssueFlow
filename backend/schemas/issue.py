from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from backend.schemas.user import UserResponse
from backend.schemas.comment import CommentResponse
from backend.schemas.activity import ActivityResponse


class IssueBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = None
    priority: str = Field(default="MEDIUM")  # LOW, MEDIUM, HIGH, CRITICAL
    issue_type: str = Field(default="BUG")   # BUG, FEATURE, TASK, IMPROVEMENT
    tags: Optional[str] = None              # "backend,api"
    due_date: Optional[datetime] = None


class IssueCreate(IssueBase):
    assignee_id: Optional[int] = None


class IssueUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = None            # OPEN, IN_PROGRESS, RESOLVED, CLOSED
    priority: Optional[str] = None
    issue_type: Optional[str] = None
    assignee_id: Optional[int] = None
    tags: Optional[str] = None
    due_date: Optional[datetime] = None


class IssueStatusUpdate(BaseModel):
    status: str = Field(..., description="Target status: OPEN, IN_PROGRESS, RESOLVED, or CLOSED")


class IssueAssigneeUpdate(BaseModel):
    assignee_id: Optional[int] = None


class IssueResponse(IssueBase):
    id: int
    issue_key: str
    status: str
    reporter_id: Optional[int] = None
    assignee_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    reporter: Optional[UserResponse] = None
    assignee: Optional[UserResponse] = None
    comments_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class IssueDetailResponse(IssueResponse):
    comments: List[CommentResponse] = []
    activities: List[ActivityResponse] = []

    model_config = ConfigDict(from_attributes=True)


class IssueListResponse(BaseModel):
    items: List[IssueResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
