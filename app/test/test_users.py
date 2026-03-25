from fastapi import status
from app.test.conftest import client,TestingSessionLocal
from app.models import User
from app.routers.auth import bcrypt_context


def test_get_user(test_user):
    response = client.get("/user/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == test_user.username
    assert data["email"] == test_user.email


def test_change_password_success(test_user):
    response = client.put(
        "/user/password",
        json={"password": "testpassword", "new_password": "newpassword123"}
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    user = db.query(User).filter(User.username == test_user.username).first()
    assert bcrypt_context.verify("newpassword123", user.hashed_password)


def test_change_password_wrong_password(test_user):
    response = client.put(
        "/user/password",
        json={"password": "wrongpassword", "new_password": "newpassword123"}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Error on password change"}


def test_delete_own_account(test_user):
    response = client.delete("/user/me")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Your account has been deleted"}

    db = TestingSessionLocal()
    user = db.query(User).filter(User.username == test_user.username).first()
    assert user is None


def test_delete_user_not_found(test_user):
    client.delete("/user/me")
    response = client.delete("/user/me")
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}