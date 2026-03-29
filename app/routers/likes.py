from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path, Request, status
from uuid import UUID
from ..models import Like,User,Post
from ..database import get_db
from .auth import get_current_user


router = APIRouter(
    prefix='/like',
    tags=['likes'])


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[User, Depends(get_current_user)]



@router.post("/post/{post_id}/like")
async def toggle_like(
    post_id: UUID,
    user: user_dependency,
    db: db_dependency
):
    #  if post exists
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # if post already liked
    existing_like = db.query(Like).filter(Like.user_id == user.id, Like.post_id == post_id).first()

    if existing_like:
        # UNLIKE
        db.delete(existing_like)
        db.commit()

        return {"message": "Post unliked"}

    else:
        # LIKE
        new_like = Like(user_id=user.id, post_id=post_id)
        
        db.add(new_like)
        db.commit()

        return {"message": "Post liked"}
    

@router.get("/post/{post_id}/like_count")
async def count_likes(post_id: UUID, db:db_dependency, user: user_dependency):
    count = db.query(Like).filter(Like.post_id == post_id).count()
    
    return{"likes": count}



@router.get("/post/{post_id}/user_like_status")
async def user_like_status(
    post_id: UUID,
    user: user_dependency,
    db: db_dependency
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    existing_like = db.query(Like).filter(Like.user_id == user.id, Like.post_id == post_id).first()
    
    return {"has_liked": existing_like is not None}