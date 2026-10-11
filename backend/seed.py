from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend.database import SessionLocal, engine, Base
from backend.models.user import User
from backend.models.issue import Issue
from backend.models.comment import Comment
from backend.models.activity import ActivityLog
from backend.core.security import hash_password


def seed_database(db: Session):
    """Seed the database with sample users, issues, comments, and activities."""
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)

    # Check if data already exists
    if db.query(User).first():
        print("Database already contains data. Skipping seed.")
        return

    print("Seeding IssueFlow database with sample data...")

    # 1. Create Demo Users
    users = [
        User(
            email="admin@issueflow.dev",
            username="admin",
            full_name="Sarah Chen (Team Lead)",
            role="admin",
            avatar_color="#6366f1",
            hashed_password=hash_password("admin123"),
            is_active=True
        ),
        User(
            email="alex@issueflow.dev",
            username="alex_dev",
            full_name="Alex Rivera (Senior Engineer)",
            role="developer",
            avatar_color="#06b6d4",
            hashed_password=hash_password("dev12345"),
            is_active=True
        ),
        User(
            email="priya@issueflow.dev",
            username="priya_qa",
            full_name="Priya Patel (QA Lead)",
            role="tester",
            avatar_color="#ec4899",
            hashed_password=hash_password("qa123456"),
            is_active=True
        ),
        User(
            email="marcus@issueflow.dev",
            username="marcus_fe",
            full_name="Marcus Vance (Frontend Dev)",
            role="developer",
            avatar_color="#10b981",
            hashed_password=hash_password("front123"),
            is_active=True
        )
    ]
    db.add_all(users)
    db.commit()

    for u in users:
        db.refresh(u)

    admin, alex, priya, marcus = users[0], users[1], users[2], users[3]

    # 2. Create Sample Issues
    now = datetime.utcnow()
    issues = [
        Issue(
            issue_key="ISF-1",
            title="JWT Session Token expiration not refreshing on client",
            description="Users report getting logged out during active sessions without a grace period or refresh handshake. Need to implement token refresh or handle expired JWT interceptors gracefully.",
            status="IN_PROGRESS",
            priority="HIGH",
            issue_type="BUG",
            reporter_id=priya.id,
            assignee_id=alex.id,
            tags="auth,security,api",
            due_date=now + timedelta(days=2)
        ),
        Issue(
            issue_key="ISF-2",
            title="Design Interactive Kanban board with drag-and-drop support",
            description="Provide an agile Kanban view alongside the table list view, grouping issues by OPEN, IN_PROGRESS, RESOLVED, and CLOSED stages with quick status transitions.",
            status="RESOLVED",
            priority="CRITICAL",
            issue_type="FEATURE",
            reporter_id=admin.id,
            assignee_id=marcus.id,
            tags="frontend,ui,kanban",
            due_date=now - timedelta(days=1)
        ),
        Issue(
            issue_key="ISF-3",
            title="SQLite concurrency locks during simultaneous burst requests",
            description="Observed 'database is locked' errors during rapid concurrent API test suites. Resolved by configuring SQLite WAL mode and timeout connect_args.",
            status="CLOSED",
            priority="HIGH",
            issue_type="BUG",
            reporter_id=alex.id,
            assignee_id=alex.id,
            tags="backend,database,sqlite",
            due_date=now - timedelta(days=3)
        ),
        Issue(
            issue_key="ISF-4",
            title="Add real-time Issue Audit History and Activity Stream",
            description="Track every change to status, priority, assignee, and comments in a dedicated audit log so team members have complete traceability on issue workflows.",
            status="IN_PROGRESS",
            priority="MEDIUM",
            issue_type="FEATURE",
            reporter_id=admin.id,
            assignee_id=alex.id,
            tags="audit,compliance,backend",
            due_date=now + timedelta(days=5)
        ),
        Issue(
            issue_key="ISF-5",
            title="Implement responsive mobile view navigation drawer",
            description="Ensure the sidebar folds cleanly into a slide-over mobile drawer on screens under 768px with touch-friendly tap targets and glassmorphic backdrop.",
            status="OPEN",
            priority="MEDIUM",
            issue_type="TASK",
            reporter_id=priya.id,
            assignee_id=marcus.id,
            tags="mobile,responsive,css",
            due_date=now + timedelta(days=7)
        ),
        Issue(
            issue_key="ISF-6",
            title="Export issue summary report to CSV and JSON format",
            description="Provide an option on the dashboard and issue list to export filtered search results into structured CSV for weekly team sprint reviews.",
            status="OPEN",
            priority="LOW",
            issue_type="IMPROVEMENT",
            reporter_id=admin.id,
            assignee_id=None,
            tags="reporting,export,tooling",
            due_date=now + timedelta(days=12)
        ),
        Issue(
            issue_key="ISF-7",
            title="Add Pydantic schema validation for empty comment bodies",
            description="Prevent submitting blank or whitespace-only comments on the issue discussion thread with custom string strip validators and 422 HTTP responses.",
            status="RESOLVED",
            priority="MEDIUM",
            issue_type="BUG",
            reporter_id=priya.id,
            assignee_id=alex.id,
            tags="validation,api,pydantic",
            due_date=now - timedelta(days=2)
        )
    ]
    db.add_all(issues)
    db.commit()

    for i in issues:
        db.refresh(i)

    # 3. Create Sample Comments
    comments = [
        Comment(
            issue_id=issues[0].id,
            author_id=priya.id,
            content="Repro steps: Log in, idle for 20 minutes, perform an issue update. The endpoint returns 401 Unauthorized."
        ),
        Comment(
            issue_id=issues[0].id,
            author_id=alex.id,
            content="Investigating the JWT verification middleware. I'm adding an auto-relogin prompt and extended token expiry settings in config."
        ),
        Comment(
            issue_id=issues[1].id,
            author_id=marcus.id,
            content="Kanban layout completed with CSS grid columns, drag styling, and responsive fallback for smaller viewports."
        ),
        Comment(
            issue_id=issues[3].id,
            author_id=admin.id,
            content="The audit activity logs are working nicely! Tested with status and assignee changes."
        )
    ]
    db.add_all(comments)
    db.commit()

    # 4. Create Activity Logs
    activities = [
        ActivityLog(
            issue_id=issues[0].id,
            user_id=priya.id,
            action_type="CREATED",
            description="Created issue ISF-1: 'JWT Session Token expiration not refreshing on client' by Priya Patel (QA Lead)"
        ),
        ActivityLog(
            issue_id=issues[0].id,
            user_id=priya.id,
            action_type="ASSIGNEE_CHANGE",
            field_changed="assignee",
            new_value="Alex Rivera (Senior Engineer)",
            description="Assigned to Alex Rivera (Senior Engineer) by Priya Patel (QA Lead)"
        ),
        ActivityLog(
            issue_id=issues[0].id,
            user_id=alex.id,
            action_type="STATUS_CHANGE",
            field_changed="status",
            old_value="OPEN",
            new_value="IN_PROGRESS",
            description="Status changed from OPEN to IN_PROGRESS by Alex Rivera (Senior Engineer)"
        ),
        ActivityLog(
            issue_id=issues[1].id,
            user_id=marcus.id,
            action_type="STATUS_CHANGE",
            field_changed="status",
            old_value="IN_PROGRESS",
            new_value="RESOLVED",
            description="Status changed from IN_PROGRESS to RESOLVED by Marcus Vance (Frontend Dev)"
        ),
        ActivityLog(
            issue_id=issues[2].id,
            user_id=alex.id,
            action_type="STATUS_CHANGE",
            field_changed="status",
            old_value="RESOLVED",
            new_value="CLOSED",
            description="Status changed from RESOLVED to CLOSED by Alex Rivera (Senior Engineer)"
        )
    ]
    db.add_all(activities)
    db.commit()
    print("Database seeding completed successfully!")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
