import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from backend.database import Base, get_db
from backend.main import app
from backend.models.user import User
from backend.core.security import hash_password, create_access_token

# In-memory SQLite test database shared across threads in memory
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh in-memory database for each test function."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Override get_db dependency with test session and return TestClient."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def admin_user(db_session):
    user = User(
        email="admin@test.dev",
        username="admin_test",
        full_name="Admin Test User",
        role="admin",
        hashed_password=hash_password("adminpass"),
        avatar_color="#6366f1",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def developer_user(db_session):
    user = User(
        email="dev@test.dev",
        username="dev_test",
        full_name="Developer Test User",
        role="developer",
        hashed_password=hash_password("devpass123"),
        avatar_color="#06b6d4",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def tester_user(db_session):
    user = User(
        email="qa@test.dev",
        username="qa_test",
        full_name="QA Test User",
        role="tester",
        hashed_password=hash_password("qapass123"),
        avatar_color="#ec4899",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_headers(admin_user):
    token = create_access_token({"sub": admin_user.email, "user_id": admin_user.id, "role": admin_user.role})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def developer_headers(developer_user):
    token = create_access_token({"sub": developer_user.email, "user_id": developer_user.id, "role": developer_user.role})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def tester_headers(tester_user):
    token = create_access_token({"sub": tester_user.email, "user_id": tester_user.id, "role": tester_user.role})
    return {"Authorization": f"Bearer {token}"}
