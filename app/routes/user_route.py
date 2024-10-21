from typing import List

from fastapi import APIRouter, Depends, status, HTTPException
from app.core.database import get_db
from app.schemas.user_schema import UserCreate, UserResponse, UserUpdate, UpdatePassword
from sqlalchemy.orm import Session
from app.utils.hashing import Hash
from ..schemas.token_schema import TokenData
from ..utils.oauth2 import get_current_user
from app.models.user_model import User
from app.schemas.api_response import APIResponse

router = APIRouter(
    prefix="/user",
    tags=['Users']
)


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=APIResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    username = db.query(User).filter(User.username == user.username).first()
    email = db.query(User).filter(User.email == user.email).first()

    if username:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail=f"Username is already exist.")

    if email:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail="Email is already exist.")

    new_user = User(first_name=user.first_name,
                    last_name=user.last_name,
                    username=user.username,
                    email=user.email,
                    password=Hash.hash_pw(user.password))

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return APIResponse(
        code=201,
        result=UserResponse(
            id=new_user.id,
            first_name=new_user.first_name,
            last_name=new_user.last_name,
            username=new_user.username,
            email=new_user.email,
        )
    )


@router.get('/all', response_model=List[UserResponse])
def get_all_user(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    # Implementing skip and limit for pagination
    all_users = db.query(User).offset(skip).limit(limit).all()

    print(all_users)

    return all_users

@router.get("/{id}", response_model=UserResponse)
def get_user_by_id(id: int,
                   current_user: TokenData = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Not found user with id = {id}")

    return user


@router.put("/{id}", response_model=UserResponse)
def update_user(id: int, user: UserUpdate,
                current_user: TokenData = Depends(get_current_user),
                db: Session = Depends(get_db)):
    user_db = db.query(User).filter(User.id == id).first()
    if not user_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Not found user with id = {id}")

    if current_user.user_id != id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not allowed to update this user")

    user_db.first_name = user.first_name
    user_db.last_name = user.last_name

    db.commit()
    db.refresh(user_db)

    return user_db


@router.put("/update-password/{id}", response_model=UserResponse)
def update_password(id: int, user: UpdatePassword,
                    current_user: TokenData = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    user_db = db.query(User).filter(User.id == id).first()
    if not user_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Not found user with id = {id}")

    if current_user.user_id != id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not allowed to update this user")

    if not Hash.verify_pw(user.old_password, user_db.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Old password is incorrect")

    if user.new_password != user.confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="New password and confirm password do not match")

    user_db.password = Hash.hash_pw(user.new_password)

    db.commit()
    db.refresh(user_db)

    return user_db
