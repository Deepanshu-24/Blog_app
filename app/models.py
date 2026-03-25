from sqlalchemy import Column, Integer, String, Boolean, ForeignKey,DateTime
from .database import Base
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
import uuid
from sqlalchemy.dialects.postgresql import UUID




class User(Base):
    __tablename__ = 'users'

    id =  Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable= False)
    username = Column(String, unique=True, nullable= False)
    hashed_password = Column(String, nullable= False)
    is_admin = Column(Boolean,default=False)
    created_at = Column(DateTime ,default = lambda: datetime.now(timezone.utc) )
    
    posts = relationship("Post" , back_populates="author", cascade="all, delete")
    likes = relationship("Like", back_populates= "user",  cascade="all, delete")
    comments = relationship("Comment", back_populates= "user",  cascade="all, delete")

class Post(Base):
    __tablename__ = "posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    image_url= Column(String, nullable= True )
    title = Column(String , nullable = False, index = True)
    content = Column(String, nullable= False )
    posted_at = Column(DateTime,default = lambda: datetime.now(timezone.utc))
    author_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False,  index=True)


    author = relationship("User",back_populates="posts" )
    likes = relationship("Like", back_populates= "post",  cascade="all, delete")
    comments = relationship("Comment", back_populates= "post", cascade="all, delete")
  

class Like(Base):
    __tablename__= "likes"

    user_id =  Column(UUID(as_uuid=True), ForeignKey("users.id"),primary_key=True)
    post_id =  Column(UUID(as_uuid=True), ForeignKey("posts.id"),primary_key=True)

    user = relationship("User", back_populates="likes")
    post = relationship("Post", back_populates= "likes")

class Comment(Base):
    __tablename__ = "comments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id"), nullable=False, index=True)

    content = Column(String(300), nullable=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")

