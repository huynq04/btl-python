from typing import Optional

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class UserResponse(BaseModel):
    activated: Optional[bool] = None
    dob: Optional[datetime] = None
    email: EmailStr
    first_name: str
    id: int
    last_name: str
    location: Optional[str] = None
    name_picture_firebase: Optional[str] = None  # Cho phép giá trị None
    phone: Optional[str] = None
    picture: Optional[str] = None
    username: str

    class Config:
        from_orm = True
        from_attributes = True


class UserCreate(BaseModel):
    username: str
    email: EmailStr = Field(..., description="Email must be a valid email address")
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    first_name: str
    last_name: str


class UserUpdate(BaseModel):
    first_name: str
    last_name: str
    dob:Optional[datetime] = None
    location: Optional[str] = None
    phone: Optional[str] = None


class UpdatePassword(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    confirm_password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
