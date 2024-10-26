from pydantic import BaseModel

class CheckOtpRequest(BaseModel):
    username:str
    otp_code:str