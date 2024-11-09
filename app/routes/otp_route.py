import smtplib
import random

from fastapi import APIRouter,Depends, HTTPException, status
from app.core.database import get_db
from app.schemas.api_response import APIResponse
from sqlalchemy.orm import Session
from app.models.user_model import User
from app.models.otp_model import Otp
from app.schemas.otp_schema import CheckOtpRequest
from datetime import datetime,timedelta

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

router = APIRouter(
    prefix="/identity/api/v1/otp",
    tags=['Otp']
)  

def send_html_email(subject, html_body, to_email):
    from_email = "haihuy9a@gmail.com"
    password = "vydookwgmkvjjwvz"

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(html_body, 'html'))

    try:
        # Kết nối tới server Gmail
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, password)
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        print("Email đã được gửi thành công!")
    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")


@router.get("/send-otp/{username}")
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
    html=f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Email HTML</title>
        </head>
        <body>
            <h1>Hello</h1>
            <p>Here is your otp code to resset passsword: {otp_code}</p>
        </body>
        </html>
    """
    send_html_email("Document PTIT - Resset password",html,user_db.email)
    return APIResponse(code=1000,result='Email sent successfully')
#đợi fix mail

@router.post("/check-otp/{username}",response_model=APIResponse)
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


