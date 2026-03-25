import uuid
from datetime import timedelta
import pytest
from fastapi import status, HTTPException
from jose import jwt
from app.test.conftest import client
from app.routers.auth import (
    authenticate_user, create_access_token, get_current_user,
    SECRET_KEY, ALGORITHM
)


def test_authenticate_user_success(db,test_user):
    user = authenticate_user(test_user.username, "testpassword", db)
    assert user is not None
    assert user.username == test_user.username


def test_authenticate_user_wrong_username(db,test_user):
    user = authenticate_user("wrongusername", "testpassword", db)
    assert user is False


def test_authenticate_user_wrong_password(db,test_user):

    user = authenticate_user(test_user.username, "wrongpassword", db)
    assert user is False


def test_create_access_token():
    username = "testuser"
    user_id = uuid.uuid4()
    is_admin = True
    expires_delta = timedelta(minutes=20)

    token = create_access_token(username, user_id, is_admin, expires_delta)
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_signature": False})

    assert payload["sub"] == username
    assert payload["id"] == str(user_id)
    assert payload["is_admin"] is is_admin


@pytest.mark.asyncio
async def test_get_current_user_valid_token(db,test_user):
    token = create_access_token(test_user.username, test_user.id, test_user.is_admin, timedelta(minutes=20))
    user = await get_current_user(token=token,db=db)
    assert user.id == test_user.id
    assert user.username == test_user.username


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(db):
    invalid_token = "this.is.not.valid"
    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(token=invalid_token,db=db)
    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "Could not validate user."


def test_create_user_endpoint():
    response = client.post(
        "/auth/",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword"
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    assert data["is_admin"] is False


def test_create_user_existing_user(test_user):
    response = client.post(
        "/auth/",
        json={
            "username": test_user.username,
            "email": test_user.email,
            "password": "testpassword"
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "User already exists"


def test_login_for_access_token_success(test_user):
    response = client.post(
        "/auth/token",
        data={"username": test_user.username, "password": "testpassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_for_access_token_wrong_credentials():
    response = client.post(
        "/auth/token",
        data={"username": "wronguser", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate user."