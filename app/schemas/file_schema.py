from pydantic import BaseModel
from typing import Optional

# Schema để thêm file (POST request)
class FileCreate(BaseModel):
    name: str
    firebase_id: Optional[str] = None
    folder: Optional[int] = None  # ID của folder nếu có

# Schema để trả về file (dùng cho các GET request và response trả về)
class FileResponse(BaseModel):
    id: int
    name: str
    slug: str
    folder: Optional[int]

    class Config:
        orm_mode = True

# Schema cho việc xoá file (DELETE request - có thể không cần thiết nếu bạn chỉ truyền ID trong URL)
class FileDelete(BaseModel):
    id: int
