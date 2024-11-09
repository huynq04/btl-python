import re

from datetime import datetime


from typing import List

from fastapi import APIRouter, Depends, status, HTTPException
from app.core.database import get_db
from app.schemas.user_schema import PictureUpdateRequest, UserCreate, UserResponse, UserUpdate, UpdatePassword
from app.schemas.password_schema import ChangePassWordRequest,ResetPasswordRequest;
from sqlalchemy.orm import Session
from app.utils.hashing import Hash
from ..schemas.token_schema import TokenData
from ..utils.oauth2 import get_current_user
from app.models.user_model import User
from app.models.otp_model import Otp
from app.schemas.api_response import APIResponse

router = APIRouter(
    prefix="/identity/users",
    tags=['Users']
)

@router.post("", status_code=status.HTTP_201_CREATED, response_model=APIResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    username = db.query(User).filter(User.username == user.username).first()
    email = db.query(User).filter(User.email == user.email).first()

    if username:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail={
                                "code":1002,
                                "message":"Username already exists"}
                            )

    if email:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail={
                                "code":1002,
                                "message":"Email already exists"
                            })

    new_user = User(first_name=user.first_name,
                    last_name=user.last_name,
                    username=user.username,
                    email=user.email,
                    activated=True,
                    password=Hash.hash_pw(user.password),
                    picture="https://raw.githubusercontent.com/huynq04/pdoc_image/refs/heads/master/avatar_default.png")

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return APIResponse(
        code=1000,
        result=UserResponse(
            id=new_user.id,
            first_name=new_user.first_name,
            last_name=new_user.last_name,
            username=new_user.username,
            email=new_user.email,
            picture=new_user.picture
        ),
    )

@router.get('/myInfo',status_code=status.HTTP_200_OK, response_model=APIResponse)
def get_my_info( current_user: TokenData = Depends(get_current_user),db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == current_user.user_id).first()
    return APIResponse(code=1000,result=UserResponse(id=user.id,first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            email=user.email,
            picture=user.picture,
            dob=user.dob,
            location=user.location,phone=user.phone,name_picture_firebase=user.name_picture_firebase,
            activated=user.activated))

# @router.get('/all', response_model=List[UserResponse])
# def get_all_user(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
#     # Implementing skip and limit for pagination
#     all_users = db.query(User).offset(skip).limit(limit).all()

#     print(all_users)

#     return all_users

# @router.get("/{id}", response_model=APIResponse)
# def get_user_by_id(id: int,
#                    current_user: TokenData = Depends(get_current_user),
#                    db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.id == id).first()
#     if not user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail=f"Not found user with id = {id}")

#     user_response = UserResponse.model_validate(user)

#     return APIResponse(
#         code=200,
#         result=user_response
#     )

@router.put("/change-password",response_model=APIResponse)
def change_password(request: ChangePassWordRequest,current_user: TokenData = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    user_db = db.query(User).filter(User.id == current_user.user_id).first()
    old_password=request.old_password
    if(Hash.verify_pw(user_db.password,old_password)):
        new_password=Hash.hash_pw(request.new_password)
        user_db.password=new_password
        db.commit()
        db.refresh(user_db)

        return APIResponse(code=1000,result={"result":"Password changed succesfully"})
    else: raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail={"code":1004,"message":"Wrong password"})

@router.put("/reset-password",response_model=APIResponse)
def reset_password(request:ResetPasswordRequest, db: Session = Depends(get_db)):
    user_db = db.query(User).filter(User.username == request.username).first()
    if(user_db is None):
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={
                                "code":"1005",
                                "message":"Cannot find username "
                            })
    otp_db=db.query(Otp).filter(Otp.user_id==user_db.id).first()
    if(otp_db):
        if(request.otp_code==otp_db.otp_code):
            if(otp_db.expiry_time<datetime.now()):
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                               detail={
                                "code":"1007",
                                "message":"Your otp code has expired"
                            })
            new_password=Hash.hash_pw(request.new_password)
            user_db.password=new_password
            db.commit()
            db.refresh(user_db)
            db.query(Otp).filter(Otp.user_id == user_db.id).delete()
            db.commit()
            return APIResponse(code=1000,result={"result":"Password changed successfully"})

        else: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                               detail={
                                "code":"1009",
                                "message":"Your otp code you entered is in valid"
                            })
    else: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                               detail={
                                "code":"1001",
                                "message":"Cannot find otp"
                            })

@router.put("/{id}", response_model=APIResponse)
def update_user(id: int, user: UserUpdate,
                current_user: TokenData = Depends(get_current_user),
                db: Session = Depends(get_db)):
    user_db = db.query(User).filter(User.id == id).first()
    if not user_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={"code":1002,"message":"User not found"})
    if current_user.user_id != id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail={"code":1001,"message":"You can't delete the profile not your own"})

    user_db.first_name = user.first_name
    user_db.last_name = user.last_name
    user_db.phone=user.phone
    user_db.location=user.location
    user_db.dob=user.dob

    db.commit()
    db.refresh(user_db)

    return APIResponse(code=1000,
                       result=UserResponse(id=user_db.id,first_name=user_db.first_name,
            last_name=user_db.last_name,
            username=user_db.username,
            email=user_db.email,
            picture=user_db.picture,
            dob=user_db.dob,
            location=user_db.location,phone=user_db.phone,name_picture_firebase=user_db.name_picture_firebase,
            activated=user_db.activated))

@router.get("/get-hidden-email/{username}")
def get_hidden_email(username:str,db: Session = Depends(get_db)):
    user_db = db.query(User).filter(User.username == username).first()
    if(user_db is None):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail={
            "code":"1009",
            "message":"Cannot find user"
        })
    if user_db.email is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={
                                "code":"1005",
                                "message":"Cannot find user 's email"
                            })
    try:
        user,domain= str(user_db.email).split('@')
        masked_user = user[-2:] if len(user) > 2 else user
        return APIResponse(code=1000,result={"email":f"***{masked_user}@{domain}"})
    except ValueError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail={"code":"9999","message":"Invalid email"})

@router.put("/update-picture/{userId}")
def update_picture(userId:int,request:PictureUpdateRequest,
                   current_user: TokenData = Depends(get_current_user),db: Session = Depends(get_db)):
    user_db = db.query(User).filter(User.id == userId).first()
    if not user_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={"code":1002,"message":"User not found"})
    if current_user.user_id != userId:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail={"code":1001,"message":"You can't update the profile not your own"})
    user_db.picture=request.link_url
    user_db.name_picture_firebase=request.name_picture_firebase

    db.commit()
    db.refresh(user_db)

    return APIResponse(code=1000,
                       result=UserResponse(id=user_db.id,first_name=user_db.first_name,
            last_name=user_db.last_name,
            username=user_db.username,
            email=user_db.email,
            picture=user_db.picture,
            dob=user_db.dob,
            location=user_db.location,phone=user_db.phone,name_picture_firebase=user_db.name_picture_firebase,
            activated=user_db.activated))
    

# @router.put("/update-password/{id}", response_model=UserResponse)
# def update_password(id: int, user: UpdatePassword,
#                     current_user: TokenData = Depends(get_current_user),
#                     db: Session = Depends(get_db)):
#     user_db = db.query(User).filter(User.id == id).first()
#     if not user_db:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail=f"Not found user with id = {id}")

#     if current_user.user_id != id:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
#                             detail="You are not allowed to update this user")

#     if not Hash.verify_pw(user.old_password, user_db.password):
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
#                             detail="Old password is incorrect")

#     if user.new_password != user.confirm_password:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
#                             detail="New password and confirm password do not match")

#     user_db.password = Hash.hash_pw(user.new_password)

#     db.commit()
#     db.refresh(user_db)

#     return user_db


