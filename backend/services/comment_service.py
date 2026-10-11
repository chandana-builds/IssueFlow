from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from backend.models.comment import Comment
from backend.models.issue import Issue
from backend.models.user import User
from backend.schemas.comment import CommentCreate
from backend.services.activity_service import ActivityService


class CommentService:
    @staticmethod
    def add_comment(db: Session, issue_id: int, user: User, comment_in: CommentCreate) -> Comment:
        issue = db.query(Issue).filter(Issue.id == issue_id).first()
        if not issue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Issue with ID {issue_id} not found"
            )

        comment = Comment(
            issue_id=issue_id,
            author_id=user.id,
            content=comment_in.content
        )
        db.add(comment)
        db.commit()
        db.refresh(comment)

        # Log activity
        ActivityService.log_activity(
            db=db,
            issue_id=issue_id,
            user_id=user.id,
            action_type="COMMENT_ADDED",
            description=f"{user.full_name} added a comment"
        )

        return comment

    @staticmethod
    def get_comments_for_issue(db: Session, issue_id: int) -> List[Comment]:
        return (
            db.query(Comment)
            .filter(Comment.issue_id == issue_id)
            .order_by(Comment.created_at.asc())
            .all()
        )

    @staticmethod
    def delete_comment(db: Session, comment_id: int, current_user: User) -> bool:
        comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )

        # Only comment author or admin can delete
        if comment.author_id != current_user.id and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this comment"
            )

        issue_id = comment.issue_id
        db.delete(comment)
        db.commit()

        # Log deletion
        ActivityService.log_activity(
            db=db,
            issue_id=issue_id,
            user_id=current_user.id,
            action_type="COMMENT_DELETED",
            description=f"{current_user.full_name} deleted a comment"
        )

        return True
