from pydantic import BaseModel
from typing import Optional

# Schema để thêm file (POST request)
class FileCreate(BaseModel):
    name: str
    firebase_id: Optional[str] = None  # Firebase ID có thể là None nếu không bắt buộc
    folder: Optional[int] = None  # ID của folder, có thể để trống

# Schema để trả về file (dùng cho các GET request và response trả về)
class FileResponse(BaseModel):
    id: int
    name: str
    slug: str
    folder: Optional[int]  # ID của folder, có thể để trống

    class Config:
        orm_mode = True  # Giúp chuyển đổi từ SQLAlchemy model sang Pydantic model dễ dàng
