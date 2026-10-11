import math
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.user import User
from backend.schemas.issue import (
    IssueCreate,
    IssueUpdate,
    IssueResponse,
    IssueDetailResponse,
    IssueListResponse,
    IssueStatusUpdate,
    IssueAssigneeUpdate,
)
from backend.services.issue_service import IssueService
from backend.core.dependencies import get_current_user

router = APIRouter(prefix="/api/issues", tags=["Issues"])


@router.post("", response_model=IssueResponse, status_code=status.HTTP_201_CREATED)
def create_issue(
    issue_in: IssueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new issue with auto-assigned issue key (e.g. ISF-101)."""
    return IssueService.create_issue(db=db, issue_in=issue_in, current_user=current_user)


@router.get("", response_model=IssueListResponse)
def list_issues(
    search: Optional[str] = Query(None, description="Search term in title, description, or key"),
    status: Optional[str] = Query(None, description="Comma-separated statuses: OPEN, IN_PROGRESS, RESOLVED, CLOSED"),
    priority: Optional[str] = Query(None, description="Comma-separated priorities: LOW, MEDIUM, HIGH, CRITICAL"),
    issue_type: Optional[str] = Query(None, description="Comma-separated types: BUG, FEATURE, TASK, IMPROVEMENT"),
    assignee_id: Optional[int] = Query(None, description="User ID of assignee or -1 for unassigned"),
    reporter_id: Optional[int] = Query(None, description="User ID of reporter"),
    tag: Optional[str] = Query(None, description="Filter by tag keyword"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("created_at_desc", description="Sort order"),
    db: Session = Depends(get_db)
):
    """List issues with multi-parameter search, filtering, and pagination."""
    items, total = IssueService.list_issues(
        db=db,
        search=search,
        status_filter=status,
        priority_filter=priority,
        issue_type_filter=issue_type,
        assignee_id=assignee_id,
        reporter_id=reporter_id,
        tag_filter=tag,
        page=page,
        page_size=page_size,
        sort_by=sort_by
    )
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }


@router.get("/{issue_id}", response_model=IssueDetailResponse)
def get_issue(issue_id: int, db: Session = Depends(get_db)):
    """Retrieve full issue detail including comments and activity timeline."""
    return IssueService.get_issue_by_id(db=db, issue_id=issue_id)


@router.put("/{issue_id}", response_model=IssueResponse)
def update_issue(
    issue_id: int,
    issue_in: IssueUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update issue properties with automatic audit log tracking."""
    return IssueService.update_issue(
        db=db,
        issue_id=issue_id,
        issue_in=issue_in,
        current_user=current_user
    )


@router.patch("/{issue_id}/status", response_model=IssueResponse)
def update_issue_status(
    issue_id: int,
    status_in: IssueStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Quickly transition issue workflow status."""
    return IssueService.update_status(
        db=db,
        issue_id=issue_id,
        new_status=status_in.status,
        current_user=current_user
    )


@router.patch("/{issue_id}/assign", response_model=IssueResponse)
def assign_issue(
    issue_id: int,
    assignee_in: IssueAssigneeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Assign or reassign an issue to a team member."""
    return IssueService.update_issue(
        db=db,
        issue_id=issue_id,
        issue_in=IssueUpdate(assignee_id=assignee_in.assignee_id),
        current_user=current_user
    )


@router.delete("/{issue_id}", status_code=status.HTTP_200_OK)
def delete_issue(
    issue_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an issue (authorized for reporter, managers, or admins)."""
    IssueService.delete_issue(db=db, issue_id=issue_id, current_user=current_user)
    return {"message": f"Issue {issue_id} successfully deleted"}
