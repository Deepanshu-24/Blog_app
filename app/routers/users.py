from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from ..models import User
from .auth import get_current_user
from passlib.context import CryptContext
from ..database import get_db


router = APIRouter(
    prefix='/user',
    tags=['user']
)


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[User, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=6)


@router.get('/', status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency):
    return user


@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, db: db_dependency,
                          user_verification: UserVerification):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    user_model = db.query(User).filter(User.id == user.id).first()

    if not bcrypt_context.verify(user_verification.password, user_model.hashed_password):
        raise HTTPException(status_code=401, detail='Error on password change')
    user_model.hashed_password = bcrypt_context.hash(user_verification.new_password)
    db.add(user_model)
    db.commit()
    db.refresh(user_model)

@router.delete("/me")
async def delete_own_account(
    current_user: user_dependency,
    db: db_dependency):

    user = db.query(User).filter(User.id == current_user.id).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    db.delete(user)
    db.commit()

    return {"message": "Your account has been deleted"}


