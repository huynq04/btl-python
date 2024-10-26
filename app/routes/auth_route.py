from fastapi import APIRouter, Depends, HTTPException, status
from app.core.database import get_db
from sqlalchemy.orm import Session
from ..models.user_model import User
from fastapi.security import OAuth2PasswordRequestForm

from ..utils import token
from ..utils.hashing import Hash


router = APIRouter(
    prefix="/auth",
    tags=['Authentication']
)

@router.post('/token')
def login(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    print(request.username)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={"code":"1005", "message":"Cannot find user"})
    if not Hash.verify_pw(user.password, request.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"code":"1006", "message":"Incorrect password"})

    access_token = token.create_access_token(data={"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}
