from typing import Optional, List, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc, func
from fastapi import HTTPException, status

from backend.models.issue import Issue
from backend.models.user import User
from backend.schemas.issue import IssueCreate, IssueUpdate
from backend.services.activity_service import ActivityService


class IssueService:
    @staticmethod
    def _next_key(db: Session) -> str:
        """Generates a readable sequential issue key like ISF-101."""
        max_id = db.query(func.max(Issue.id)).scalar() or 0
        return f"ISF-{max_id + 1}"

    @staticmethod
    def create_issue(db: Session, issue_in: IssueCreate, current_user: User) -> Issue:
        issue_key = IssueService._next_key(db)
        
        # Verify assignee exists if provided
        assignee = None
        if issue_in.assignee_id:
            assignee = db.query(User).filter(User.id == issue_in.assignee_id).first()
            if not assignee:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Assignee with ID {issue_in.assignee_id} does not exist"
                )

        issue = Issue(
            issue_key=issue_key,
            title=issue_in.title.strip(),
            description=issue_in.description,
            status="OPEN",
            priority=issue_in.priority.upper(),
            issue_type=issue_in.issue_type.upper(),
            reporter_id=current_user.id,
            assignee_id=issue_in.assignee_id,
            tags=issue_in.tags,
            due_date=issue_in.due_date
        )
        db.add(issue)
        db.commit()
        db.refresh(issue)

        # Log creation
        ActivityService.log_activity(
            db=db,
            issue_id=issue.id,
            user_id=current_user.id,
            action_type="CREATED",
            description=f"Created issue {issue.issue_key}: '{issue.title}' by {current_user.full_name}"
        )

        if assignee:
            ActivityService.log_activity(
                db=db,
                issue_id=issue.id,
                user_id=current_user.id,
                action_type="ASSIGNEE_CHANGE",
                field_changed="assignee",
                new_value=assignee.full_name,
                description=f"Assigned to {assignee.full_name} by {current_user.full_name}"
            )

        return issue

    @staticmethod
    def get_issue_by_id(db: Session, issue_id: int) -> Issue:
        issue = db.query(Issue).filter(Issue.id == issue_id).first()
        if not issue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Issue with ID {issue_id} not found"
            )
        # Attach comment count helper attribute
        issue.comments_count = len(issue.comments)
        return issue

    @staticmethod
    def get_issue_by_key(db: Session, key: str) -> Issue:
        issue = db.query(Issue).filter(Issue.issue_key == key.upper()).first()
        if not issue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Issue with key {key} not found"
            )
        issue.comments_count = len(issue.comments)
        return issue

    @staticmethod
    def list_issues(
        db: Session,
        search: Optional[str] = None,
        status_filter: Optional[str] = None,
        priority_filter: Optional[str] = None,
        issue_type_filter: Optional[str] = None,
        assignee_id: Optional[int] = None,
        reporter_id: Optional[int] = None,
        tag_filter: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
        sort_by: str = "created_at_desc"
    ) -> Tuple[List[Issue], int]:
        query = db.query(Issue)

        if search:
            search_term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    Issue.title.ilike(search_term),
                    Issue.description.ilike(search_term),
                    Issue.issue_key.ilike(search_term),
                    Issue.tags.ilike(search_term)
                )
            )

        if status_filter and status_filter.upper() != "ALL":
            statuses = [s.strip().upper() for s in status_filter.split(",")]
            query = query.filter(Issue.status.in_(statuses))

        if priority_filter and priority_filter.upper() != "ALL":
            priorities = [p.strip().upper() for p in priority_filter.split(",")]
            query = query.filter(Issue.priority.in_(priorities))

        if issue_type_filter and issue_type_filter.upper() != "ALL":
            types = [t.strip().upper() for t in issue_type_filter.split(",")]
            query = query.filter(Issue.issue_type.in_(types))

        if assignee_id is not None:
            if assignee_id == -1:  # Sentinel for unassigned
                query = query.filter(Issue.assignee_id == None)
            else:
                query = query.filter(Issue.assignee_id == assignee_id)

        if reporter_id is not None:
            query = query.filter(Issue.reporter_id == reporter_id)

        if tag_filter:
            query = query.filter(Issue.tags.ilike(f"%{tag_filter.strip()}%"))

        # Sorting
        if sort_by == "created_at_asc":
            query = query.order_by(asc(Issue.created_at))
        elif sort_by == "priority_desc":
            # Critical > High > Medium > Low
            query = query.order_by(desc(Issue.priority))
        elif sort_by == "updated_at_desc":
            query = query.order_by(desc(Issue.updated_at))
        else:
            query = query.order_by(desc(Issue.created_at))

        total = query.count()
        offset = (page - 1) * page_size
        items = query.offset(offset).limit(page_size).all()

        for item in items:
            item.comments_count = len(item.comments)

        return items, total

    @staticmethod
    def update_issue(
        db: Session,
        issue_id: int,
        issue_in: IssueUpdate,
        current_user: User
    ) -> Issue:
        issue = db.query(Issue).filter(Issue.id == issue_id).first()
        if not issue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Issue with ID {issue_id} not found"
            )

        # Track modifications for activity logs
        changes = []

        if issue_in.title is not None and issue_in.title.strip() != issue.title:
            changes.append(("title", issue.title, issue_in.title.strip()))
            issue.title = issue_in.title.strip()

        if issue_in.description is not None and issue_in.description != issue.description:
            changes.append(("description", "...", "..."))
            issue.description = issue_in.description

        if issue_in.status is not None:
            new_status = issue_in.status.upper()
            if new_status != issue.status:
                changes.append(("status", issue.status, new_status))
                issue.status = new_status

        if issue_in.priority is not None:
            new_priority = issue_in.priority.upper()
            if new_priority != issue.priority:
                changes.append(("priority", issue.priority, new_priority))
                issue.priority = new_priority

        if issue_in.issue_type is not None:
            new_type = issue_in.issue_type.upper()
            if new_type != issue.issue_type:
                changes.append(("issue_type", issue.issue_type, new_type))
                issue.issue_type = new_type

        if issue_in.tags is not None and issue_in.tags != issue.tags:
            changes.append(("tags", issue.tags or "none", issue_in.tags))
            issue.tags = issue_in.tags

        if issue_in.due_date is not None and issue_in.due_date != issue.due_date:
            changes.append(("due_date", str(issue.due_date), str(issue_in.due_date)))
            issue.due_date = issue_in.due_date

        if issue_in.assignee_id is not None or "assignee_id" in issue_in.model_fields_set:
            if issue_in.assignee_id != issue.assignee_id:
                old_assignee_name = issue.assignee.full_name if issue.assignee else "Unassigned"
                if issue_in.assignee_id is None:
                    new_assignee_name = "Unassigned"
                    issue.assignee_id = None
                else:
                    new_assignee = db.query(User).filter(User.id == issue_in.assignee_id).first()
                    if not new_assignee:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Assignee ID {issue_in.assignee_id} does not exist"
                        )
                    new_assignee_name = new_assignee.full_name
                    issue.assignee_id = new_assignee.id
                changes.append(("assignee", old_assignee_name, new_assignee_name))

        db.commit()
        db.refresh(issue)

        # Log individual field activities
        for field, old_val, new_val in changes:
            action = "UPDATED"
            if field == "status":
                action = "STATUS_CHANGE"
                desc_text = f"Status changed from {old_val} to {new_val} by {current_user.full_name}"
            elif field == "priority":
                action = "PRIORITY_CHANGE"
                desc_text = f"Priority changed from {old_val} to {new_val} by {current_user.full_name}"
            elif field == "assignee":
                action = "ASSIGNEE_CHANGE"
                desc_text = f"Assignee updated to {new_val} by {current_user.full_name}"
            else:
                desc_text = f"Updated {field} by {current_user.full_name}"

            ActivityService.log_activity(
                db=db,
                issue_id=issue.id,
                user_id=current_user.id,
                action_type=action,
                field_changed=field,
                old_value=str(old_val),
                new_value=str(new_val),
                description=desc_text
            )

        issue.comments_count = len(issue.comments)
        return issue

    @staticmethod
    def update_status(db: Session, issue_id: int, new_status: str, current_user: User) -> Issue:
        valid_statuses = ["OPEN", "IN_PROGRESS", "RESOLVED", "CLOSED"]
        target = new_status.upper()
        if target not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status '{new_status}'. Allowed: {valid_statuses}"
            )
        return IssueService.update_issue(
            db=db,
            issue_id=issue_id,
            issue_in=IssueUpdate(status=target),
            current_user=current_user
        )

    @staticmethod
    def delete_issue(db: Session, issue_id: int, current_user: User) -> bool:
        issue = db.query(Issue).filter(Issue.id == issue_id).first()
        if not issue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Issue with ID {issue_id} not found"
            )

        # Only reporter, manager, or admin can delete
        if issue.reporter_id != current_user.id and current_user.role not in ["admin", "manager"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to delete this issue"
            )

        db.delete(issue)
        db.commit()
        return True
