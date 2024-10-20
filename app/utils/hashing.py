from passlib.context import CryptContext

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Hash:
    def hash_pw(password: str):
        return password_context.hash(password)

    def verify_pw(hashed_pw: str, plain_pw):
        return password_context.verify(plain_pw, hashed_pw)
