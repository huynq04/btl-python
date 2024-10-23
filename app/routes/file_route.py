from fastapi import APIRouter, HTTPException, Depends, status
from app.schemas.api_response import APIResponse
from app.schemas.file_schema import FileCreate, FileResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.document_model import Document
from app.models.folder_model import Folder
from app.schemas.folder_schema import FolderResponse
from ..schemas.token_schema import TokenData
from ..utils.oauth2 import get_current_user

router = APIRouter(
    prefix="/file",
    tags=['File']
)

# API: Lấy file theo slug.py
@router.get("/{slug}", response_model=APIResponse)
def get_file_by_slug(slug: str, current_user: TokenData = Depends(get_current_user), db: Session = Depends(get_db)):
    folder = db.query(Folder).filter(Folder.slug == slug).first()

    if not folder:
        raise HTTPException(status_code=404, detail="Folder không tồn tại")

    documents = db.query(Document).filter(Document.folder_id == folder.id).all()

    if not documents:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài liệu trong folder")

    items = []
    for document in documents:
        items.append({
            "id": str(document.id),
            "name": document.name,
            "firebaseId": document.firebase_id,
            "createAt": document.create_at,
            "folder": {
                "id": str(folder.id),
                "name": folder.name,
                "view": folder.view,
                "star": folder.star,
                "createAt": folder.create_at,
                "slug": folder.slug,
                "author": {
                    "id": str(folder.author.id),
                    "username": folder.author.username,
                    "firstName": folder.author.first_name,
                    "lastName": folder.author.last_name,
                    "dob": folder.author.dob,
                    "picture": folder.author.picture,
                    "location": folder.author.location,
                    "phone": folder.author.phone,
                    "email": folder.author.email,
                    "noPassword": folder.author.no_password,
                    "activated": folder.author.activated,
                }
            }
        })

    return APIResponse(
        code=1000,
        result={
            "items": items,
            "total": len(items),
            "canUpdate": True
        }
    )



@router.post("/add/{slug}", response_model=APIResponse)
def add_file(slug: str, file_data: FileCreate,
             current_user: TokenData = Depends(get_current_user),
             db: Session = Depends(get_db)):
    folder = db.query(Folder).filter(Folder.slug == slug).first()

    if not folder:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Folder không tồn tại")

    new_file = Document(name=file_data.name, firebase_id=file_data.firebase_id, folder_id=folder.id)


    db.add(new_file)
    db.commit()
    db.refresh(new_file)

    folder_response = FolderResponse(
        create_at=folder.create_at,
        id=folder.id,
        name=folder.name,
        slug=folder.slug,
        star=folder.star,
        view=folder.view,
        author=folder.author
    )

    return APIResponse(
        code=200,
        result=FileResponse(
            id=new_file.id,
            name=new_file.name,
            firebase_id=new_file.firebase_id,
            create_at=new_file.create_at,
            folder=folder_response 
        )
    )

# API: Lấy document theo id
@router.get("/document/{id}", response_model=APIResponse)
def get_document_by_id(id: int,current_user: TokenData = Depends(get_current_user), db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == id).first()

    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document không tồn tại")

    return APIResponse(
        code=200,
        result=FileResponse(
            id=document.id,
            name=document.name,
            firebase_id=document.firebase_id,
            create_at=document.create_at,
            folder=FolderResponse(
                create_at=document.folder.create_at,
                id=document.folder.id,
                name=document.folder.name,
                slug=document.folder.slug,
                star=document.folder.star,
                view=document.folder.view,
                author=document.folder.author
            )
        )
    )

# API: Xóa document theo id
@router.delete("/document/{id}")
def delete_document_by_id(id: int,current_user: TokenData = Depends(get_current_user), db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document không tồn tại")
    db.delete(document)
    db.commit()
    return {"message": "Document đã được xóa"}

# API: Xóa tất cả các document
@router.delete("/document")
def delete_all_documents(current_user: TokenData = Depends(get_current_user),db: Session = Depends(get_db)):
    db.query(Document).delete()
    db.commit()
    return {"message": "Tất cả document đã được xóa"}