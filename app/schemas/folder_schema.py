from typing import Optional, List, Union
from pydantic import BaseModel
from datetime import datetime
from app.schemas.user_schema import UserResponse  
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship


class FolderResponse(BaseModel):
    create_at: datetime
    id: int
    liked: Optional[bool] = False  
    name: str
    slug: str
    star: int
    view: int
    author: UserResponse  

    class Config:
        from_attributes = True  


class FolderCreate(BaseModel):
    name: str  

class FolderDeleteRequest(BaseModel):
    slug:str 
    
