from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.user import User
from backend.schemas.comment import CommentCreate, CommentResponse
from backend.services.comment_service import CommentService
from backend.core.dependencies import get_current_user

router = APIRouter(tags=["Comments"])


@router.post("/api/issues/{issue_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def add_comment(
    issue_id: int,
    comment_in: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Post a new comment on an issue and record in the audit log."""
    return CommentService.add_comment(
        db=db,
        issue_id=issue_id,
        user=current_user,
        comment_in=comment_in
    )


@router.get("/api/issues/{issue_id}/comments", response_model=List[CommentResponse])
def get_comments(
    issue_id: int,
    db: Session = Depends(get_db)
):
    """List all comments associated with an issue."""
    return CommentService.get_comments_for_issue(db=db, issue_id=issue_id)


@router.delete("/api/comments/{comment_id}", status_code=status.HTTP_200_OK)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a comment (author or admin only)."""
    CommentService.delete_comment(db=db, comment_id=comment_id, current_user=current_user)
    return {"message": "Comment deleted successfully"}
