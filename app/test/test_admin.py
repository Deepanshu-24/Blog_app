import uuid
from fastapi import status
from app.models import Post, Comment
from app.test.conftest import client
from app.main import app
from app.routers.auth import get_current_user


def test_get_all_users(test_user):
    response = client.get("/admin/users")
    assert response.status_code == status.HTTP_200_OK
    users = response.json()
    assert any(user["email"] == test_user.email for user in users)


def test_delete_post(db,test_post):
    response = client.delete(f"/admin/post/{test_post.id}")
    assert response.status_code == 204

    post = db.query(Post).filter(Post.id == test_post.id).first()
    db.close()
    assert post is None


def test_delete_post_not_found(test_user):
    response = client.delete(f"/admin/post/{uuid.uuid4()}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Post not found."}


def test_delete_comment(db,test_comment):
    response = client.delete(f"/admin/comments/{test_comment.id}")
    assert response.status_code == 204

    comment = db.query(Comment).filter(Comment.id == test_comment.id).first()
    db.close()
    assert comment is None


def test_delete_comment_not_found(test_user):
    response = client.delete(f"/admin/comments/{uuid.uuid4()}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Comment not found"}


def test_non_admin_cannot_access_users(non_admin_user):
    # Temporarily override current user with a non-admin
    original_override = app.dependency_overrides.get(get_current_user)

    def override_non_admin():
        return non_admin_user

    app.dependency_overrides[get_current_user] = override_non_admin
    response = client.get("/admin/users")

    assert response.status_code == 403
    assert response.json() == {"detail": "Admin access required"}

    # Restore original override
    if original_override:
        app.dependency_overrides[get_current_user] = original_override