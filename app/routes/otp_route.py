import random

from fastapi import APIRouter,Depends, HTTPException, status
from app.core.database import get_db
from app.schemas.api_response import APIResponse
from sqlalchemy.orm import Session
from app.models.user_model import User
from app.models.otp_model import Otp
from app.schemas.otp_schema import CheckOtpRequest
from datetime import datetime,timedelta

router = APIRouter(
    prefix="/identity/api/v1/otp",
    tags=['Otp']
)    

@router.get("/send-otp/{username}",response_model=APIResponse)
def send_otp(username:str,  db: Session = Depends(get_db)):
    user_db = db.query(User).filter(User.username == username).first()
    if user_db.email is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail={
                                "code":"9999",
                                "message":"Cannot send email"
                            })
    otp_code = f"{random.randint(0, 999999):06d}"
    expiry_time=datetime.now() + timedelta(minutes=5)
    otp_db=Otp(otp_code=otp_code,expiry_time=expiry_time,user_id=user_db.id)
    db.query(Otp).filter(Otp.user_id == user_db.id).delete()
    db.add(otp_db)
    db.commit()
    db.refresh(otp_db)
    return APIResponse(code=1000)
#đợi fix mail

@router.get("/check-otp/{username}",response_model=APIResponse)
def check_otp(username:str,request: CheckOtpRequest, db: Session = Depends(get_db)):
    user_db = db.query(User).filter(User.username == username).first()
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
            return APIResponse(code=1000,result={"result":"Verified successfully"})

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

