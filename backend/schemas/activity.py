from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from backend.schemas.user import UserResponse


class ActivityResponse(BaseModel):
    id: int
    issue_id: int
    user_id: Optional[int] = None
    action_type: str
    field_changed: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    description: str
    created_at: datetime
    user: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)
