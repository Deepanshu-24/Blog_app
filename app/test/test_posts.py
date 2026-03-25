from fastapi import status
from app.test.conftest import client,TestingSessionLocal
from app.models import Post
import uuid


def test_read_all_posts(test_post):
    response = client.get("/posts/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1


def test_read_single_post(test_post):
    response = client.get(f"/posts/{test_post.id}")
    assert response.status_code == status.HTTP_200_OK


def test_read_single_post_not_found():
    response = client.get(f"/posts/{uuid.uuid4()}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Post not found."}


def test_create_post(test_user):
    response = client.post(
        "/posts/",
        data={"title": "New Post", "content": "New Content"}
    )
    assert response.status_code == 201

    db = TestingSessionLocal()
    post = db.query(Post).filter(Post.title == "New Post").first()
    assert post is not None
    db.close()


def test_update_post(test_post):
    response = client.put(
        f"/posts/{test_post.id}",
        json={"title": "Updated Title", "content": "Updated Content", "image_url": None}
    )
    assert response.status_code == 200

    db = TestingSessionLocal()
    post = db.query(Post).filter(Post.id == test_post.id).first()
    assert post.title == "Updated Title"
    db.close()


def test_update_post_not_found():
    response = client.put(
        f"/posts/{uuid.uuid4()}",
        json={"title": "Updated", "content": "Updated", "image_url": None}
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Post not found"}


def test_delete_post(test_post):
    response = client.delete(f"/posts/{test_post.id}")
    assert response.status_code == 204

    db = TestingSessionLocal()
    post = db.query(Post).filter(Post.id == test_post.id).first()
    assert post is None
    db.close()


def test_delete_post_not_found():
    response = client.delete(f"/posts/{uuid.uuid4()}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Post not found"}