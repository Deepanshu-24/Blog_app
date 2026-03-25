import uuid
from fastapi import status
from app.models import Comment
from app.test.conftest import client,app,override_current_user

# Override current user dependency for all tests in this module
def setup_module(module):
    from app.routers.posts import get_current_user
    app.dependency_overrides[get_current_user] = override_current_user


def test_create_comment(db,test_post):
    response = client.post(
        f"/comment/post/{test_post.id}/comment",
        json={"content": "This is a test comment"}
    )

    assert response.status_code == status.HTTP_200_OK

    comment = db.query(Comment).filter(Comment.post_id == test_post.id).first()
    db.close()

    assert comment is not None
    assert comment.content == "This is a test comment"


def test_create_comment_post_not_found():
    response = client.post(
        f"/comment/post/{uuid.uuid4()}/comment",
        json={"content": "Test comment"}
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Post not found"}


def test_update_comment(db,test_post):
    # create comment first
    create_resp = client.post(
        f"/comment/post/{test_post.id}/comment",
        json={"content": "Old content"}
    )
    comment_id = uuid.UUID(create_resp.json()["id"])

    # update
    update_resp = client.put(
        f"/comment/comments/{comment_id}",
        json={"content": "Updated content"}
    )

    assert update_resp.status_code == 200
    assert update_resp.json()["content"] == "Updated content"

    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    db.close()
    assert comment.content == "Updated content"


def test_update_comment_not_found():
    response = client.put(
        f"/comment/comments/{uuid.uuid4()}",
        json={"content": "Updated content"}
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Comment not found"}


def test_delete_comment(db, test_post):
    # create comment
    create_resp = client.post(
        f"/comment/post/{test_post.id}/comment",
        json={"content": "To be deleted"}
    )
    comment_id = uuid.UUID(create_resp.json()["id"])

    # delete
    delete_resp = client.delete(f"/comment/comments/{comment_id}")
    assert delete_resp.status_code == 204

    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    db.close()
    assert comment is None


def test_delete_comment_not_found():
    response = client.delete(f"/comment/comments/{uuid.uuid4()}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Comment not found"}