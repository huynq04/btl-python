from fastapi import APIRouter, Depends, status, HTTPException
from app.core.database import get_db
from app.models.user_model import User
from app.schemas.folder_schema import FolderCreate, FolderResponse
from sqlalchemy.orm import Session
from ..utils.oauth2 import get_current_user
from app.schemas.api_response import APIResponse
from ..schemas.token_schema import TokenData
from app.models.folder_model import Folder
from ..utils.slug import generate_slug

router = APIRouter(
    prefix="/folder",
    tags=['Folder']
)


@router.post("/add", status_code=status.HTTP_201_CREATED, response_model=APIResponse)
def create_folder(folder: FolderCreate,
                current_user: TokenData = Depends(get_current_user),
                db: Session = Depends(get_db)):
    name_folder =  db.query(Folder).filter(Folder.name == folder.name).first()
    if name_folder:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail=f"Folder name is already exist.")
    
    slug = generate_slug(folder.name)

    new_folder = Folder(name=folder.name,
                        author_id=current_user.user_id,
                        slug=slug)
    db.add(new_folder)
    db.commit()
    db.refresh(new_folder)

    author = db.query(User).filter(User.id == new_folder.author_id).first()

    return APIResponse(
        code=201,
        result=FolderResponse(
            id=new_folder.id,
            name=new_folder.name,
            user_id=new_folder.author_id,
            view=new_folder.view,
            slug=new_folder.slug,
            star=new_folder.star,
            liked = False,
            create_at=new_folder.create_at,
            author = author
        )
    )





