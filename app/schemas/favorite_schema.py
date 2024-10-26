from pydantic import BaseModel

class FavoriteResponse(BaseModel):
    folder_id: int
    user_id: int

    class Config:
        orm_mode = True  # Đảm bảo có cấu hình này
