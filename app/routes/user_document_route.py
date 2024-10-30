from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.folder_model import Folder
from app.models.user_folder_model import User_Folder
from app.schemas.api_response import APIResponse
from app.schemas.token_schema import TokenData
from app.utils.oauth2 import get_current_user


router = APIRouter(
    prefix="/identity/users/my-documents",
    tags=["My-documents"]
)

@router.get("",response_model=APIResponse)
def get_my_folder_list(page:int = 1, limit: int = 8, current_user: TokenData = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    skip = (page - 1) * limit
    query=db.query(Folder).filter(Folder.author_id==current_user.user_id)
    folders=[]
    fs = query.offset(skip).limit(limit).all()
    for f in fs:
        folders.append({
            "id": f.id,
            "name": f.name,
            "slug": f.slug,
            "star": f.star,
            "view": f.view,
            "create_at":f.create_at,
            "author": {
                "id": f.author.id,
                "username": f.author.username,
                "email": f.author.email,
            },
            "liked":db.query(User_Folder).filter(
                User_Folder.user_id == current_user.user_id,
                User_Folder.folder_id == f.id
            ).first() is not None
        })
    return APIResponse(code=1000,result={"items":folders,"total":query.count()})