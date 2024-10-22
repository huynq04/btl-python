from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from app.schemas.user_schema import UserResponse

class FolderResponse(BaseModel):
    create_at: datetime
    id: int
    liked: Optional[bool] = None
    name: str
    slug: str
    star: int
    view: int

    author: UserResponse


class FolderCreate(BaseModel):
    name: str
