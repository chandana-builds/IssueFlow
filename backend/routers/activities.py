from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas.activity import ActivityResponse
from backend.services.activity_service import ActivityService

router = APIRouter(tags=["Activity Logs"])


@router.get("/api/issues/{issue_id}/activities", response_model=List[ActivityResponse])
def get_issue_activities(
    issue_id: int,
    db: Session = Depends(get_db)
):
    """Retrieve full audit log for a specific issue."""
    return ActivityService.get_activities_for_issue(db=db, issue_id=issue_id)


@router.get("/api/activities/recent", response_model=List[ActivityResponse])
def get_recent_activities(
    limit: int = Query(15, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Retrieve global recent project activities for the dashboard activity stream."""
    return ActivityService.get_recent_activities(db=db, limit=limit)
