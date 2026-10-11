from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.models.issue import Issue
from backend.models.user import User
from backend.schemas.dashboard import DashboardStatsResponse
from backend.services.activity_service import ActivityService


class StatsService:
    @staticmethod
    def get_dashboard_stats(db: Session, current_user: Optional[User] = None) -> DashboardStatsResponse:
        total = db.query(func.count(Issue.id)).scalar() or 0
        
        # Status counts
        status_rows = db.query(Issue.status, func.count(Issue.id)).group_by(Issue.status).all()
        status_map = {"OPEN": 0, "IN_PROGRESS": 0, "RESOLVED": 0, "CLOSED": 0}
        for s_name, count in status_rows:
            if s_name:
                status_map[s_name.upper()] = count

        # Priority counts
        priority_rows = db.query(Issue.priority, func.count(Issue.id)).group_by(Issue.priority).all()
        priority_map = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
        for p_name, count in priority_rows:
            if p_name:
                priority_map[p_name.upper()] = count

        # Type counts
        type_rows = db.query(Issue.issue_type, func.count(Issue.id)).group_by(Issue.issue_type).all()
        type_map = {"BUG": 0, "FEATURE": 0, "TASK": 0, "IMPROVEMENT": 0}
        for t_name, count in type_rows:
            if t_name:
                type_map[t_name.upper()] = count

        resolved_count = status_map.get("RESOLVED", 0) + status_map.get("CLOSED", 0)
        res_rate = round((resolved_count / total * 100), 1) if total > 0 else 0.0

        # Overdue count
        now = datetime.utcnow()
        overdue_count = (
            db.query(func.count(Issue.id))
            .filter(
                Issue.due_date != None,
                Issue.due_date < now,
                Issue.status.notin_(["RESOLVED", "CLOSED"])
            )
            .scalar() or 0
        )

        # Recent activities
        recent_acts = ActivityService.get_recent_activities(db, limit=10)

        # Personal metrics if authenticated
        my_assigned_open = 0
        my_reported_total = 0
        if current_user:
            my_assigned_open = (
                db.query(func.count(Issue.id))
                .filter(
                    Issue.assignee_id == current_user.id,
                    Issue.status.notin_(["RESOLVED", "CLOSED"])
                )
                .scalar() or 0
            )
            my_reported_total = (
                db.query(func.count(Issue.id))
                .filter(Issue.reporter_id == current_user.id)
                .scalar() or 0
            )

        return DashboardStatsResponse(
            total_issues=total,
            open_issues=status_map.get("OPEN", 0),
            in_progress_issues=status_map.get("IN_PROGRESS", 0),
            resolved_issues=status_map.get("RESOLVED", 0),
            closed_issues=status_map.get("CLOSED", 0),
            resolution_rate_percent=res_rate,
            overdue_issues=overdue_count,
            status_counts=status_map,
            priority_counts=priority_map,
            type_counts=type_map,
            recent_activities=recent_acts,
            my_assigned_open=my_assigned_open,
            my_reported_total=my_reported_total
        )
