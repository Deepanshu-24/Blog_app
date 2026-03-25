from fastapi import status
from app.test.conftest import client,TestingSessionLocal
from app.models import Like
import uuid


def test_like_post(test_post):
    response = client.post(f"/like/post/{test_post.id}/like")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Post liked"}

    db = TestingSessionLocal()
    like = db.query(Like).filter(Like.post_id == test_post.id).first()
    assert like is not None
    db.close()


def test_unlike_post(test_post):
    client.post(f"/like/post/{test_post.id}/like")
    response = client.post(f"/like/post/{test_post.id}/like")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Post unliked"}

    db = TestingSessionLocal()
    like = db.query(Like).filter(Like.post_id == test_post.id).first()
    assert like is None
    db.close()


def test_like_post_not_found():
    response = client.post(f"/like/post/{uuid.uuid4()}/like")
    assert response.status_code == 404
    assert response.json() == {"detail": "Post not found"}


def test_like_count(test_post):
    response = client.get(f"/like/post/{test_post.id}/like_count")
    assert response.status_code == 200
    assert response.json() == {"likes": 0}

    client.post(f"/like/post/{test_post.id}/like")
    response = client.get(f"/like/post/{test_post.id}/like_count")
    assert response.json() == {"likes": 1}

    client.post(f"/like/post/{test_post.id}/like")
    response = client.get(f"/like/post/{test_post.id}/like_count")
    assert response.json() == {"likes": 0}