from datetime import datetime
from fastapi import APIRouter, Depends, status, HTTPException
from app.core.database import get_db
from app.models.user_folder_model import User_Folder
from app.models.user_model import User
from app.schemas.folder_schema import FolderCreate, FolderDeleteRequest, FolderResponse
from sqlalchemy.orm import Session
from ..utils.oauth2 import get_current_user
from app.schemas.api_response import APIResponse
from ..schemas.token_schema import TokenData
from app.models.folder_model import Folder
from ..utils.slug import generate_slug

router = APIRouter(
    prefix="/identity/api/v1/folder",
    tags=['Folder']
)


@router.post("/add", status_code=status.HTTP_201_CREATED, response_model=APIResponse)
def create_folder(
    folder: FolderCreate,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db), 
):
    
    slug = generate_slug(folder.name.strip().lower().replace(" ", "-"))

    existing_folder = db.query(Folder).filter(Folder.slug == slug).first()
    if existing_folder:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"code": 1010,"message": "Folder already exists: A folder with this name already exists"})

    new_folder = Folder(
        name=folder.name,
        author_id=current_user.user_id,
        slug=slug,
        create_at=datetime.now(),
        view=0,
        star=0
    )



    db.add(new_folder)
    db.commit()
    db.refresh(new_folder)

    author = db.query(User).filter(User.id == new_folder.author_id).first()

    return APIResponse(
        code=1000,
        result=FolderResponse(
            id=new_folder.id,
            name=new_folder.name,
            user_id=new_folder.author_id,
            view=new_folder.view,
            slug=new_folder.slug,
            star=new_folder.star,
            create_at=new_folder.create_at,
            author=author,
            liked = False,
        )
    )



@router.get("/", response_model=APIResponse)
def get_folders(page: int = 1,  current_user: TokenData = Depends(get_current_user),limit: int = 8, db: Session = Depends(get_db)):
    skip = (page - 1) * limit
    query=db.query(Folder)
    folders=[]
    fs = query.order_by(Folder.create_at.desc()).offset(skip).limit(limit).all()
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
                "picture":f.author.picture,
                "first_name": f.author.first_name,
                "last_name": f.author.last_name,
            },
            "liked":db.query(User_Folder).filter(
                User_Folder.user_id == current_user.user_id,
                User_Folder.folder_id == f.id
            ).first() is not None
        })
    return APIResponse(code=1000,result={"items":folders,"total":query.count()})




@router.delete("/delete", response_model=APIResponse)
def delete_folder(
    folder_del:FolderDeleteRequest,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    folder = db.query(Folder).filter(Folder.slug == folder_del.slug).first()

    if not folder:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={"code": 1009,"message": "Folder not found: No folder exists with the provided slug"})

    if folder.author_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail={"code": 1007,"message": "Not allowed to delete this folder: You do not have permission to delete this folder"})
    

    db.delete(folder)
    db.commit()

    return APIResponse(
        code=1000,
        result={"message": f"Folder with slug {folder.slug} has been deleted"}
    )









