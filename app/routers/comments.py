from typing import Annotated, List
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path, Request, status
from uuid import UUID
from ..models import Like,User,Post,Comment
from ..database import get_db
from .auth import get_current_user
from pydantic import BaseModel,Field
from datetime import datetime,timezone

router = APIRouter(
    prefix='/comment',
    tags=['comments'])


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[User, Depends(get_current_user)]


class CommentRequest(BaseModel):
    content: str = Field(min_length=3, max_length=100)

class CommentResponse(BaseModel):
    id: UUID
    content: str
    user_id: UUID
    post_id: UUID
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True



@router.post("/post/{post_id}/comment", response_model=CommentResponse)
async def comment(
    post_id: UUID,
    user: user_dependency,
    db: db_dependency,
    comment_request : CommentRequest
):
    #  if post exists
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    comment_model = Comment(**comment_request.model_dump(), user_id=user.id, post_id = post_id)

    db.add(comment_model)
    db.commit()
    db.refresh(comment_model)

    return comment_model


@router.put("/comments/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: UUID,
    user: user_dependency,
    db: db_dependency,
    comment_request: CommentRequest):

    comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if comment.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this comment")

    comment.content = comment_request.content
    comment.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(comment)

    return comment


@router.delete("/comments/{comment_id}", status_code=204)
async def delete_comment(
    comment_id: UUID,
    user: user_dependency,
    db: db_dependency
):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if comment.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")

    db.delete(comment)
    db.commit()

@router.get("/post/{post_id}/comments", response_model=List[CommentResponse])
def get_comments_for_post(post_id: UUID, db: Session = Depends(get_db)):
    comments = db.query(Comment).filter(Comment.post_id == post_id).all()
    return comments
