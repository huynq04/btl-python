from fastapi import APIRouter, HTTPException, Depends, status
from app.schemas.api_response import APIResponse
from app.schemas.file_schema import FileCreate, FileResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.document_model import Document
from app.models.folder_model import Folder
from app.schemas.folder_schema import FolderResponse

router = APIRouter(
    prefix="/file",
    tags=['File']
)

# API: Lấy file theo slug.py
@router.get("/{slug}", response_model=FileResponse)
def get_file_by_slug(slug: str, db: Session = Depends(get_db)):
    file = db.query(Document).filter(Document.slug == slug).first()
    if not file:
        raise HTTPException(status_code=404, detail="File không tồn tại")
    return file

@router.post("/add/{slug}", response_model=APIResponse)
def add_file(slug: str, file_data: FileCreate, db: Session = Depends(get_db)):
    folder = db.query(Folder).filter(Folder.slug == slug).first()

    if not folder:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Folder không tồn tại")
    
    new_file = Document(name=file_data.name, firebase_id=file_data.firebase_id, folder_id = folder.id)

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
@router.get("/document/{id}", response_model=FileResponse)
def get_document_by_id(id: int, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document không tồn tại")
    return document

# API: Xóa document theo id
@router.delete("/document/{id}")
def delete_document_by_id(id: int, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document không tồn tại")
    db.delete(document)
    db.commit()
    return {"message": "Document đã được xóa"}

# API: Xóa tất cả các document
@router.delete("/document")
def delete_all_documents(db: Session = Depends(get_db)):
    db.query(Document).delete()
    db.commit()
    return {"message": "Tất cả document đã được xóa"}