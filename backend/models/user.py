from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from backend.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(150), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="developer", nullable=False)  # admin, manager, developer, tester
    avatar_color = Column(String(20), default="#6366f1", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    reported_issues = relationship(
        "Issue",
        foreign_keys="Issue.reporter_id",
        back_populates="reporter"
    )
    assigned_issues = relationship(
        "Issue",
        foreign_keys="Issue.assignee_id",
        back_populates="assignee"
    )
    comments = relationship(
        "Comment",
        back_populates="author",
        cascade="all, delete-orphan"
    )
    activities = relationship(
        "ActivityLog",
        back_populates="user"
    )
