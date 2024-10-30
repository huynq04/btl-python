from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.folder_model import Folder
from app.models.user_folder_model import User_Folder
from app.schemas.api_response import APIResponse
from ..schemas.token_schema import TokenData
from ..utils.oauth2 import get_current_user

router = APIRouter(
    prefix="/identity/users/my-favorites",
    tags=["Favorites"]
)


@router.put("/add/{id}", response_model=APIResponse)
def add_favorite(id: int,
                 current_user: TokenData = Depends(get_current_user),
                 db: Session = Depends(get_db)):
    # Kiểm tra folder tồn tại
    folder = db.query(Folder).filter(Folder.id == id).first()
    if not folder:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail= {
                                "code": 1002,
                                "message": "Folder not found",
                            })

    # Kiểm tra nếu folder đã trong favorites của người dùng
    existing_favorite = db.query(User_Folder).filter(User_Folder.user_id == current_user.user_id,
                                                  User_Folder.folder_id == id).first()
    if existing_favorite:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={
                                "code": 1002,
                                "message": "Folder already in favorites",
                            })

    # Thêm folder vào favorites
    new_favorite = User_Folder(user_id=current_user.user_id, folder_id=id)
    db.add(new_favorite)
    db.commit()

    return APIResponse(
        code=1000,
        result={"result": "add to favourite successfully"}
    )

@router.delete("/delete/{id}", response_model=APIResponse)
def delete_favorite(id: int,
                    current_user: TokenData = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    # Kiểm tra nếu folder trong favorites của người dùng
    favorite = db.query(User_Folder).filter(User_Folder.user_id == current_user.user_id,
                                         User_Folder.folder_id == id).first()
    if not favorite:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail= {
                                "code": 1002,
                                "message": "Folder not found",
                            })

    # Xóa folder khỏi favorites
    db.delete(favorite)
    db.commit()

    return APIResponse(
        code=1000,
        result={"result": f"Folder with id {id} has been removed from favorites"}
    )

@router.get("", response_model=APIResponse)
def get_favorites(page:int = 1, limit: int = 8, current_user: TokenData = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    # Lấy tất cả các folder mà người dùng đã yêu thích
    skip = (page - 1) * limit
    query=db.query(User_Folder).filter(User_Folder.user_id == current_user.user_id)

    favorites = query.offset(skip).limit(limit).all()

    total = query.count()
    
    data = [
        {
            "id": favorite.folder.id,
            "name": favorite.folder.name,
            "slug": favorite.folder.slug,
            "star": favorite.folder.star,
            "view": favorite.folder.view,
            "create_at":favorite.folder.create_at,
            "author": {
                "id": favorite.folder.author.id,
                "username": favorite.folder.author.username,
                "email": favorite.folder.author.email,
            },
            "liked":True
        } for favorite in favorites
    ]
    

    return APIResponse(
        code=1000,
        result={
            "items": data,
            "total": total
        }  
    )
