from fastapi import APIRouter, HTTPException, Depends
from models.document_model import Document
from schemas.file_schema import FileCreate, FileResponse  # Giả sử bạn đã tạo các schema này
from sqlalchemy.orm import Session
from core.database import get_db

router = APIRouter()

# API: Lấy file theo slug
@router.get("/file/{slug}", response_model=FileResponse)
def get_file_by_slug(slug: str, db: Session = Depends(get_db)):
    file = db.query(Document).filter(Document.slug == slug).first()
    if not file:
        raise HTTPException(status_code=404, detail="File không tồn tại")
    return file

# API: Thêm file theo slug
@router.post("/file/add/{slug}", response_model=FileResponse)
def add_file(slug: str, file_data: FileCreate, db: Session = Depends(get_db)):
    new_file = Document(slug=slug, **file_data.dict())
    db.add(new_file)
    db.commit()
    db.refresh(new_file)
    return new_file

# API: Lấy document theo id
@router.get("/file/document/{id}", response_model=FileResponse)
def get_document_by_id(id: int, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document không tồn tại")
    return document

# API: Xóa document theo id
@router.delete("/file/document/{id}")
def delete_document_by_id(id: int, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document không tồn tại")
    db.delete(document)
    db.commit()
    return {"message": "Document đã được xóa"}

# API: Xóa tất cả các document
@router.delete("/file/document")
def delete_all_documents(db: Session = Depends(get_db)):
    db.query(Document).delete()
    db.commit()
    return {"message": "Tất cả document đã được xóa"}