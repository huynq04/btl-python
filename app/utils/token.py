from datetime import datetime, timedelta
from jose import JWTError, jwt
from app.schemas.token_schema import TokenData
from app.core.config_env import ACCESS_TOKEN_EXPIRE, ALGORITHM, SECRET_KEY


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now() + timedelta(days=int(ACCESS_TOKEN_EXPIRE))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        role: str = payload.get("role")
        if user_id is None:
            raise credentials_exception

        token_data = TokenData(user_id=user_id, role=role)
        return token_data
    except JWTError:
        print("JWTError")
        raise credentials_exception
