import pytest


def test_register_user_success(client):
    response = client.post("/api/auth/register", json={
        "email": "newuser@test.dev",
        "username": "newuser",
        "full_name": "New Team Member",
        "password": "securepassword123",
        "role": "developer"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@test.dev"
    assert data["username"] == "newuser"
    assert data["role"] == "developer"
    assert "id" in data
    assert "hashed_password" not in data


def test_register_duplicate_email(client, developer_user):
    response = client.post("/api/auth/register", json={
        "email": developer_user.email,
        "username": "uniqueusername",
        "full_name": "Duplicate Tester",
        "password": "securepassword123"
    })
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_login_success(client, developer_user):
    response = client.post("/api/auth/login", json={
        "email_or_username": developer_user.email,
        "password": "devpass123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == developer_user.email


def test_login_invalid_password(client, developer_user):
    response = client.post("/api/auth/login", json={
        "email_or_username": developer_user.email,
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    assert "Invalid email/username or password" in response.json()["detail"]


def test_get_current_user_me(client, developer_headers, developer_user):
    response = client.get("/api/auth/me", headers=developer_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == developer_user.id
    assert data["username"] == developer_user.username


def test_get_current_user_unauthorized(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_list_all_users(client, admin_user, developer_user):
    response = client.get("/api/auth/users")
    assert response.status_code == 200
    users = response.json()
    assert len(users) >= 2
    emails = [u["email"] for u in users]
    assert admin_user.email in emails
    assert developer_user.email in emails
