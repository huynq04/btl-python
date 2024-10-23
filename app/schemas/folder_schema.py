from typing import Optional, List, Union
from pydantic import BaseModel
from datetime import datetime
from app.schemas.user_schema import UserResponse  # Giả định bạn đã có UserResponse

# Schema cho phản hồi chi tiết folder
class FolderResponse(BaseModel):
    create_at: datetime
    id: int
    liked: Optional[bool] = False  # Thông tin người dùng có thích folder này không
    name: str
    slug: str
    star: int
    view: int
    author: UserResponse  # Thông tin tác giả (sử dụng UserResponse)

    class Config:
        orm_mode = True  # Cho phép Pydantic sử dụng dữ liệu từ SQLAlchemy model

# Schema cho việc tạo folder
class FolderCreate(BaseModel):
    name: str  # Tên folder, đây là thông tin yêu cầu khi tạo folder

# Schema chung cho phản hồi API
class APIResponse(BaseModel):
    code: int
    result: Union[FolderResponse, List[FolderResponse], dict]  # Trả về một Folder, danh sách Folder, hoặc message đơn giản
