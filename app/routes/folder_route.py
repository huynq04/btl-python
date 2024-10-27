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
    prefix="/identity/api/v1/folder",
    tags=['Folder']
)


@router.post("/add", status_code=status.HTTP_201_CREATED, response_model=APIResponse)
def create_folder(
    folder: FolderCreate,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
    page:int = 1, 
    limit:int = 4, 
    name_folder = ''
):
    name_folder = db.query(Folder).filter(Folder.name == folder.name).first()

    if name_folder:
        raise HTTPException(status_code=status.HTTP_400_NOT_ACCEPTABLE,
                            detail={"code": 1010,"message": "Folder already exists: A folder with this name already exists"})
    

    slug = generate_slug(folder.name)

    new_folder = Folder(
        name=folder.name,
        author_id=current_user.user_id,
        slug=slug
    )
    db.add(new_folder)
    db.commit()
    db.refresh(new_folder)

    # Tìm kiếm thư mục dựa trên tham số name
    skip = (page - 1) * limit
    query = db.query(Folder).filter(Folder.name.like(f"%{name}%"))
    
    fs = query.offset(skip).limit(limit).all()
    folders = [{"id": f.id, "name": f.name, "slug": f.slug} for f in fs]

    # Kiểm tra xem người dùng có thích thư mục này không
    user_folder_entry = db.query(User_Folder).filter(User_Folder.user_id == current_user.user_id,User_Folder.folder_id == new_folder.id).first()
    is_favorited = user_folder_entry is not None

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
            is_favorited=is_favorited
        )
    )



@router.get("/", response_model=APIResponse)
def get_folders(db: Session = Depends(get_db)):
    get_folder: get_folders
    current_user: TokenData = Depends(get_current_user),

    page: int = Query(1, ge=1),  
    limit: int = Query(8, ge=1),  
    offset = (page - 1) * limit

    folders = db.query(Folder).all()

    if not folders:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={"code": 1009,"message": "No folders found: No folders exist in the system"})
    
    folder_list = []
    for folder in folders:
        # Kiểm tra xem người dùng có thích thư mục này không
        user_folder_entry = db.query(User_Folder).filter(User_Folder.user_id == current_user.user_id,User_Folder.folder_id == folder.id).first()
        is_favorited = user_folder_entry is not None
    

    folder_list = [
        FolderResponse(
            id=folder.id,
            name=folder.name,
            user_id=folder.author_id,
            view=folder.view,
            slug=folder.slug,
            star=folder.star,
            create_at=folder.create_at,
            author=db.query(User).filter(User.id == folder.author_id).first(),
            is_favorited=is_favorited
        ) for folder in folders
    ]

    return APIResponse(
        code=1000,
        result=folder_list
    )




@router.delete("/delete/{folder_id}", response_model=APIResponse)
def delete_folder(
    folder_id: int,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    folder = db.query(Folder).filter(Folder.id == folder_id).first()

    if not folder:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={"code": 1009,"message": "Folder not found: No folder exists with the provided ID"})

    if folder.author_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail={"code": 1007,"message": "Not allowed to delete this folder: You do not have permission to delete this folder"})
    

    db.delete(folder)
    db.commit()

    return APIResponse(
        code=1000,
        result={"message": f"Folder with id {folder_id} has been deleted"}
    )









