from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.folder_model import Folder
from app.models.user_model import User
from app.models.favorite_model import Favorite
from app.schemas.api_response import APIResponse
from ..schemas.token_schema import TokenData
from ..utils.oauth2 import get_current_user
from pydantic import BaseModel

# Schema cho response
class FavoriteResponse(BaseModel):
    folder_id: int
    user_id: int

    class Config:
        orm_mode = True

# Router cho Favorites
router = APIRouter(
    prefix="/identity/users/my-favorites",
    tags=["Favorites"]
)

# Endpoint thêm folder vào favorites
@router.put("/add/{id}", response_model=APIResponse)
def add_favorite(id: int,
                 current_user: TokenData = Depends(get_current_user),
                 db: Session = Depends(get_db)):
    # Kiểm tra folder tồn tại
    folder = db.query(Folder).filter(Folder.id == id).first()
    if not folder:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Folder not found")

    # Kiểm tra nếu folder đã trong favorites của người dùng
    existing_favorite = db.query(Favorite).filter(Favorite.user_id == current_user.user_id,
                                                  Favorite.folder_id == id).first()
    if existing_favorite:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Folder already in favorites")

    # Thêm folder vào favorites
    new_favorite = Favorite(user_id=current_user.user_id, folder_id=id)
    db.add(new_favorite)
    db.commit()

    return APIResponse(
        code=200,
        result={"message": f"Folder with id {id} has been added to favorites"}
    )

# Endpoint xóa folder khỏi favorites
@router.delete("/delete/{id}", response_model=APIResponse)
def delete_favorite(id: int,
                    current_user: TokenData = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    # Kiểm tra nếu folder trong favorites của người dùng
    favorite = db.query(Favorite).filter(Favorite.user_id == current_user.user_id,
                                         Favorite.folder_id == id).first()
    if not favorite:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Favorite not found")

    # Xóa folder khỏi favorites
    db.delete(favorite)
    db.commit()

    return APIResponse(
        code=200,
        result={"message": f"Folder with id {id} has been removed from favorites"}
    )

# Endpoint lấy danh sách folder đã yêu thích
@router.get("/", response_model=APIResponse)
def get_favorites(current_user: TokenData = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    # Lấy tất cả các folder mà người dùng đã yêu thích
    favorites = db.query(Favorite).filter(Favorite.user_id == current_user.user_id).all()

    if not favorites:
        return APIResponse(
            code=200,
            result={"message": "No favorites found"}
        )

    # Tạo danh sách các folder từ favorites
    favorite_list = [
        FavoriteResponse(
            folder_id=favorite.folder_id,
            user_id=favorite.user_id
        ) for favorite in favorites
    ]

    return APIResponse(
        code=200,
        result=favorite_list
    )

# Mô hình Favorite (nếu chưa có, thêm vào file models)
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Favorite(Base):
    __tablename__ = 'favorites'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    folder_id = Column(Integer, ForeignKey('folders.id'))

    user = relationship("User", back_populates="favorites")
    folder = relationship("Folder", back_populates="favorites")

# Cần chỉnh sửa lại model User và Folder để hỗ trợ quan hệ với Favorite
# Trong models/user_model.py thêm:
class User(Base):
    # ...
    favorites = relationship("Favorite", back_populates="user")

# Trong models/folder_model.py thêm:
class Folder(Base):
    # ...
    favorites = relationship("Favorite", back_populates="folder")
