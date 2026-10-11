from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from backend.models.user import User
from backend.schemas.user import UserRegister
from backend.core.security import hash_password, verify_password


class AuthService:
    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email.lower()).first()

    @staticmethod
    def get_by_username(db: Session, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username.lower()).first()

    @staticmethod
    def register_user(db: Session, user_in: UserRegister) -> User:
        # Check if email exists
        if AuthService.get_by_email(db, user_in.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email already exists"
            )
        
        # Check if username exists
        if AuthService.get_by_username(db, user_in.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username is already taken"
            )

        hashed_pw = hash_password(user_in.password)
        db_user = User(
            email=user_in.email.lower(),
            username=user_in.username.lower(),
            full_name=user_in.full_name,
            hashed_password=hashed_pw,
            role=user_in.role or "developer",
            avatar_color=user_in.avatar_color or "#6366f1",
            is_active=True
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def authenticate_user(db: Session, email_or_username: str, password: str) -> Optional[User]:
        query = email_or_username.lower()
        user = db.query(User).filter(
            (User.email == query) | (User.username == query)
        ).first()

        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    def get_all_users(db: Session) -> List[User]:
        return db.query(User).filter(User.is_active == True).order_by(User.full_name.asc()).all()
