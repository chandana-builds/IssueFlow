from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.user import User
from backend.schemas.dashboard import DashboardStatsResponse
from backend.services.stats_service import StatsService
from backend.core.dependencies import get_optional_current_user

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStatsResponse)
def get_dashboard_statistics(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """Retrieve comprehensive issue metrics, breakdown charts data, and recent activities."""
    return StatsService.get_dashboard_stats(db=db, current_user=current_user)
