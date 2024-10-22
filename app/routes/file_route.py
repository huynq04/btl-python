from fastapi import APIRouter, HTTPException, Depends
from app.schemas.file_schema import FileCreate, FileResponse  # Giả sử bạn đã tạo các schema này
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.document_model import Document
from app.models.folder_model import Folder

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
    try:
        # Kiểm tra xem folder có tồn tại không
        if file_data.folder is not None:
            folder_exists = db.query(Folder).filter(Folder.id == file_data.folder).first()
            if not folder_exists:
                # Nếu không tồn tại, tạo mới một folder
                new_folder = Folder(id=file_data.folder, name="Tên Folder")  # Thay đổi tên folder theo nhu cầu
                db.add(new_folder)
                db.commit()  # Lưu folder mới vào database

        # Tiếp tục thêm file
        new_file = Document(slug=slug, **file_data.dict())
        db.add(new_file)
        db.commit()
        db.refresh(new_file)
        return new_file
    except Exception as e:
        print(f"Error occurred: {e}")  # In ra lỗi
        raise HTTPException(status_code=500, detail="Internal Server Error")

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