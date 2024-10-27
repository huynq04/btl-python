from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.folder_model import Folder
from app.schemas.api_response import APIResponse
from app.schemas.token_schema import TokenData
from app.utils.oauth2 import get_current_user

router = APIRouter(
    prefix="/identity/api/v1/search",
    tags=["Search"]
)

@router.get("",response_model=APIResponse)
def search_data(page:int = 1, limit: int = 4, name: str='', current_user: TokenData = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    skip = (page - 1) * limit
    query=db.query(Folder).filter(Folder.name.like(f"%{name}%"))
    folders=[]
    if name: 
        fs = query.offset(skip).limit(limit).all()
        for f in fs:
            folders.append({"id":f.id,"name":f.name,"slug":f.slug})

    return APIResponse(code=1000,result={"items":folders,"total":query.count()})
    