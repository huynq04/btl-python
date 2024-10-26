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
from .models import Folder, User, Likes

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
                        detail=APIResponse(
                            code=1002,
                            message="Folder existed",
                            error_message="Folder name already exists"
                        ))

    
    slug = generate_slug(folder.name)

    new_folder = Folder(name=folder.name,
                        author_id=current_user.user_id,
                        slug=slug)
    db.add(new_folder)
    db.commit()
    db.refresh(new_folder)

    liked = db.query(Likes).filter(
        Likes.user_id == current_user.user_id,
        Likes.folder_id == new_folder.id
    ).first() is not None

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
            liked = liked,
            create_at=new_folder.create_at,
            author = author
        )
    )


@router.get("/", response_model=APIResponse)
def get_folders(db: Session = Depends(get_db)):
    folders = db.query(Folder).all()

    if not folders:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=APIResponse(
                            code=1003,
                            message="No folders found",
                            error_message="No folders exist in the system"
                        ))

    folder_list = [
        FolderResponse(
            id=folder.id,
            name=folder.name,
            user_id=folder.author_id,
            view=folder.view,
            slug=folder.slug,
            star=folder.star,
            liked=db.query(Likes).filter(
                Likes.user_id == current_user.user_id,
                Likes.folder_id == folder.id
            ).first() is not None,  
            create_at=folder.create_at,
            author=db.query(User).filter(User.id == folder.author_id).first()  
        ) for folder in folders
    ]

    return APIResponse(
        code=200,
        result=folder_list
    )



@router.delete("/delete/{folder_id}", response_model=APIResponse)
def delete_folder(folder_id: int,
                  current_user: TokenData = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    folder = db.query(Folder).filter(Folder.id == folder_id).first()

    if not folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=APIResponse(
                code=1004,
                message="Folder not found",
                error_message="No folder exists with the provided ID"
            ))

     if folder.author_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=APIResponse(
                code=1005,
                message="Not allowed to delete this folder",
                error_message="You do not have permission to delete this folder"
            ))

    db.delete(folder)
    db.commit()

    return APIResponse(
        code=200,
        result={"message": f"Folder with id {folder_id} has been deleted"}
    )







