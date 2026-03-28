from typing import Annotated,List
from pydantic import BaseModel, Field, HttpUrl
from sqlalchemy.orm import Session
from sqlalchemy import desc
from fastapi import APIRouter, Depends, HTTPException, Path, status, UploadFile,File,Form
from ..models import Post,User
from ..database import get_db
from .auth import get_current_user
from typing import Optional
from uuid import UUID
from datetime import datetime,timezone
from ..config import cloudinary
import cloudinary.uploader





router = APIRouter(
    prefix='/posts',
    tags=['posts']
)


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[User, Depends(get_current_user)]


class PostRequest(BaseModel):
    title : str = Field(min_length=3)
    content : str = Field(min_length=3, max_length=1000)
    image_url: Optional[HttpUrl] = None
    
class PostFeedResponse(BaseModel):
    id: UUID
    title: str
    content: str
    image_url: Optional[str]
    author_id: UUID
    posted_at: datetime
    author_username: str

    class Config:
        from_attributes = True

class PostResponse(BaseModel):
    id: UUID
    title: str
    content: str
    image_url: Optional[str]
    author_id: UUID
    posted_at: datetime

    class Config:
        from_attributes = True


@router.get("/", response_model=List[PostResponse], status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    return db.query(Post).filter(Post.author_id == user.id).all()



@router.get("/feed", response_model=List[PostFeedResponse])
async def get_feed(db: db_dependency, user : user_dependency, limit:int=10 , offset:int=0):

    posts = db.query(Post).order_by(desc(Post.posted_at)).limit(limit).offset(offset).all()

    return [PostFeedResponse(
            id=post.id,
            title=post.title,
            content=post.content,
            image_url=post.image_url,
            posted_at=post.posted_at,
            author_id=post.author.id,
            author_username=post.author.username
        )
        for post in posts
    ]


@router.get("/{post_id}", response_model=PostResponse)
async def read_posts(user: user_dependency, db: db_dependency, post_id: UUID ):

    post = db.query(Post).filter(Post.id == post_id)\
        .filter(Post.author_id == user.id).first()
    if post is not None:
        return post
    raise HTTPException(status_code=404, detail='Post not found.')


@router.post("/",  response_model=PostResponse, status_code=201)
async def create_post(
    user: user_dependency,
    db: db_dependency,
    title: str = Form(...),
    content: str = Form(...),
    file: Optional[UploadFile] = File(None)
):
    image_url = None

    if file:
        if file.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
            raise HTTPException(status_code=400, detail="Invalid image type")

        try:
            result = cloudinary.uploader.upload(file.file)
            image_url = result["secure_url"]
        except Exception:
            raise HTTPException(status_code=500, detail="Image upload failed")

    # Create post
    post = Post(
        title=title,
        content=content,
        image_url=image_url,
        author_id=user.id,
        posted_at=datetime.now(timezone.utc)
    )

    db.add(post)
    db.commit()
    db.refresh(post)

    return post


@router.put("/{post_id}", response_model= PostResponse)
async def update_post(user: user_dependency, db: db_dependency,
                      post_request : PostRequest ,
                      post_id:UUID):

    post_model = db.query(Post).filter(Post.id == post_id).filter(Post.author_id == user.id).first()

    if post_model is None:
        raise HTTPException(status_code=404, detail="Post not found")

    post_model.title = post_request.title
    post_model.content = post_request.content
    post_model.image_url = post_request.image_url

    db.commit()
    db.refresh(post_model)

    return post_model


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(user: user_dependency, db: db_dependency,post_id : UUID):

    post_model = db.query(Post).filter(Post.id == post_id).filter(Post.author_id == user.id).first()

    if post_model is None:
        raise HTTPException(status_code=404, detail="Post not found")
    
    db.delete(post_model)

    db.commit()
