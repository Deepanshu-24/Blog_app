from ..database import get_db
from fastapi import APIRouter, Depends, HTTPException,status
from pydantic import BaseModel,Field
from sqlalchemy.orm import Session
from datetime import timedelta, datetime, timezone
from typing import Annotated
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from..models import User
from uuid import UUID
import uuid
import os

ACCESS_TOKEN_EXPIRE_MINUTES= 20


router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

db_dependency = Annotated[Session, Depends(get_db)]

class CreateUserRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: str
    password: str = Field(min_length=5)

class UserResponse(BaseModel):
    id: UUID
    username: str
    email: str
    is_admin: bool

    class Config:
        from_attributes = True  


class Token(BaseModel):
    access_token: str
    token_type: str


def authenticate_user(username: str, password: str, db):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

def create_access_token(username: str, user_id: UUID, is_admin: bool, expires_delta: timedelta):
    encode = {'sub': username, 'id': str(user_id), 'is_admin': is_admin}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)], db :db_dependency):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: uuid.UUID = uuid.UUID(payload.get("id"))
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not validate user.')
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="User not found"
    )
        return user
    
    except (JWTError, ValueError, TypeError):
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate user.'
    )


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def create_user(
    create_user_request: CreateUserRequest,
    db: db_dependency
):
    # if user already exists
    existing_user = db.query(User).filter(
        (User.email == create_user_request.email) |
        (User.username == create_user_request.username)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="User already exists"
        )

    # Create user
    create_user_model = User(
        email=create_user_request.email,
        username=create_user_request.username,
        is_admin=False,
        hashed_password=bcrypt_context.hash(create_user_request.password)
    )

    db.add(create_user_model)
    db.commit()
    db.refresh(create_user_model)

    return create_user_model

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.', headers={"WWW-Authenticate": "Bearer"})
    token = create_access_token(user.username, user.id, user.is_admin, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

    return {'access_token': token, 'token_type': 'bearer'}

