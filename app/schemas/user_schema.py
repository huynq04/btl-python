from pydantic import BaseModel, EmailStr, Field


class UserResponse(BaseModel):
    id: int
    username: str
    first_name: str
    last_name: str
    email: str
    picture: str | None


class UserCreate(BaseModel):
    username: str
    email: EmailStr = Field(..., description="Email must be a valid email address")
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    first_name: str
    last_name: str


class UserUpdate(BaseModel):
    first_name: str
    last_name: str


class UpdatePassword(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    confirm_password: str = Field(..., min_length=8, description="Password must be at least 8 characters")




