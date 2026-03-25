import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.database import Base
from app.models import User, Post
from app.routers.posts import get_db, get_current_user
from app.routers.auth import bcrypt_context

SQLALCHEMY_DATABASE_URL = "sqlite:///./testdb.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


client = TestClient(app)



def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def test_user():
    db = TestingSessionLocal()
    db.query(User).delete()
    db.commit()
    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        username="testuser",
        hashed_password=bcrypt_context.hash("testpassword"),
        is_admin=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user

@pytest.fixture
def non_admin_user():
    db = TestingSessionLocal()
    user = User(
        id=uuid.uuid4(),
        email="user@example.com",
        username="normaluser",
        hashed_password="irrelevant",
        is_admin=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user

@pytest.fixture
def test_post(test_user):
    db = TestingSessionLocal()
    post = Post(
        title="Test Post",
        content="Test Content",
        author_id=test_user.id
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    db.close()
    return post

@pytest.fixture
def test_comment(test_post):
    from app.models import Comment
    db = TestingSessionLocal()
    comment = Comment(
        content="Test Comment",
        post_id=test_post.id,
        user_id=uuid.uuid4()
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    db.close()
    return comment


@pytest.fixture(autouse=True)
def override_current_user(test_user):
    async def _override(db=None):
        return test_user
    app.dependency_overrides[get_current_user] = _override