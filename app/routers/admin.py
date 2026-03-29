from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from ..models import User,Post,Comment
from ..database import get_db
from .auth import get_current_user
from uuid import UUID

router = APIRouter(
    prefix='/admin',
    tags=['admin']
)

def admin_required(user: user_dependency):
    if not user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    return user


admin_dependency = Annotated[User, Depends(admin_required)]

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[User, Depends(get_current_user)]


@router.get("/users", status_code=status.HTTP_200_OK)
async def all_users(admin:admin_dependency, db:db_dependency):
    
    return db.query(User).all()



@router.delete("/post/{post_id}", status_code=204)
async def delete_post(admin:admin_dependency, db: db_dependency, post_id: UUID ):

    post_model = db.query(Post).filter(Post.id == post_id).first()

    if post_model is None:
        raise HTTPException(status_code=404, detail='Post not found.')
    
    db.delete(post_model)
    db.commit()
    return {"message": "Post deleted by admin"}

@router.delete("/comments/{comment_id}", status_code=204)
async def delete_comment(
    comment_id: UUID,
    admin: admin_dependency,
    db: db_dependency
):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    db.delete(comment)
    db.commit()
    return {"message": "comment deleted by admin"}

@router.delete("/user/{user_id}", status_code=204)
async def delete_user(admin:admin_dependency, db: db_dependency, user_id: UUID ):

    user_model = db.query(User).filter(User.id == user_id).first()

    if user_model is None:
        raise HTTPException(status_code=404, detail='User not found.')
    
    db.delete(user_model)
    db.commit()
    return {"message": "User deleted by admin"}