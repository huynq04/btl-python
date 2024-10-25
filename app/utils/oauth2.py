from fastapi import Depends, HTTPException, status,Request
from fastapi.security import OAuth2PasswordBearer
from . import token

class CustomOAuth2PasswordBearer(OAuth2PasswordBearer):
    async def __call__(self, request: Request):
        try:
            token = await super().__call__(request)
            return token
        except HTTPException as e:
            raise HTTPException(
                status_code=401,
                detail={"code": "1006", "message": "Not authenticated"}
            )
        
oauth2_scheme = CustomOAuth2PasswordBearer(tokenUrl="auth/token")


def get_current_user(data: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"code":"1006","message":"Could not validate credentials"},
        headers={"WWW-Authenticate": "Bearer"},
    )
    print('------------------------------------------')
    print(credentials_exception)

    return token.verify_token(data, credentials_exception)
