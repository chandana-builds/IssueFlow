from typing import Dict, List, Any
from pydantic import BaseModel
from backend.schemas.activity import ActivityResponse


class DashboardStatsResponse(BaseModel):
    total_issues: int
    open_issues: int
    in_progress_issues: int
    resolved_issues: int
    closed_issues: int
    resolution_rate_percent: float
    overdue_issues: int
    
    # Breakdowns
    status_counts: Dict[str, int]
    priority_counts: Dict[str, int]
    type_counts: Dict[str, int]
    
    # Activity and personal metrics
    recent_activities: List[ActivityResponse] = []
    my_assigned_open: int = 0
    my_reported_total: int = 0
