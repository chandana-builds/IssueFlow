from typing import Optional, List
from sqlalchemy.orm import Session
from backend.models.activity import ActivityLog


class ActivityService:
    @staticmethod
    def log_activity(
        db: Session,
        issue_id: int,
        user_id: Optional[int],
        action_type: str,
        description: str,
        field_changed: Optional[str] = None,
        old_value: Optional[str] = None,
        new_value: Optional[str] = None
    ) -> ActivityLog:
        """Helper to create and persist an audit activity log entry."""
        log = ActivityLog(
            issue_id=issue_id,
            user_id=user_id,
            action_type=action_type,
            field_changed=field_changed,
            old_value=str(old_value) if old_value is not None else None,
            new_value=str(new_value) if new_value is not None else None,
            description=description
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log

    @staticmethod
    def get_activities_for_issue(db: Session, issue_id: int) -> List[ActivityLog]:
        return (
            db.query(ActivityLog)
            .filter(ActivityLog.issue_id == issue_id)
            .order_by(ActivityLog.created_at.desc())
            .all()
        )

    @staticmethod
    def get_recent_activities(db: Session, limit: int = 15) -> List[ActivityLog]:
        return (
            db.query(ActivityLog)
            .order_by(ActivityLog.created_at.desc())
            .limit(limit)
            .all()
        )
