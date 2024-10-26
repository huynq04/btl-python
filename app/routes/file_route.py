from fastapi import APIRouter, HTTPException, Depends, status
from app.schemas.api_response import APIResponse
from app.schemas.file_schema import FileCreate, FileResponse, DeleteListDocumentsRequest, FileDeleteResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.document_model import Document
from app.models.folder_model import Folder
from app.schemas.folder_schema import FolderResponse
from ..schemas.token_schema import TokenData
from ..utils.oauth2 import get_current_user


router = APIRouter(
    prefix="/identity/api/v1/file",
    tags=['File']
)

# API: Get file by slug
@router.get("/{slug}", response_model=APIResponse)
def get_file_by_slug(slug: str, current_user: TokenData = Depends(get_current_user), db: Session = Depends(get_db)):
    folder = db.query(Folder).filter(Folder.slug == slug).first()

    if not folder:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={"code": 1009, "message": "Folder does not exist"})

    documents = db.query(Document).filter(Document.folder_id == folder.id).order_by(Document.id.desc()).all()

    items = []
    for document in documents:
        items.append({
            "id": str(document.id),
            "name": document.name,
            "fire_base_id": document.firebase_id,
            "create_at": document.create_at,
            "folder": {
                "id": str(folder.id),
                "name": folder.name,
                "view": folder.view,
                "star": folder.star,
                "create_at": folder.create_at,
                "slug": folder.slug,
                "author": {
                    "id": str(folder.author.id),
                    "username": folder.author.username,
                    "first_name": folder.author.first_name,
                    "last_name": folder.author.last_name,
                    "dob": folder.author.dob,
                    "picture": folder.author.picture,
                    "location": folder.author.location,
                    "phone": folder.author.phone,
                    "email": folder.author.email,
                    "activated": folder.author.activated,
                }
            }
        })

    can_update = folder.author_id == current_user.user_id

    return APIResponse(
        code=1000,
        result={
            "items": items,
            "total": len(items),
            "can_update": can_update
        }
    )


# API: Add file to folder
@router.post("/add/{slug}", response_model=APIResponse)
def add_file(slug: str, file_data: FileCreate,
             current_user: TokenData = Depends(get_current_user),
             db: Session = Depends(get_db)):
    folder = db.query(Folder).filter(Folder.slug == slug).first()

    if not folder:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={"code": 1009, "message": "Folder does not exist"})

    if folder.author_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail={"code": 1007, "message": "You are not authorized to add files to this folder"})

    existing_file = db.query(Document).filter(Document.firebase_id == file_data.firebase_id).first()
    if existing_file:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"code": 1010, "message": "firebase_id already exists in the documents"})

    new_file = Document(
        name=file_data.name,
        firebase_id=file_data.firebase_id,
        folder_id=folder.id
    )

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
        code=1000,
        result=FileResponse(
            id=new_file.id,
            name=new_file.name,
            firebase_id=new_file.firebase_id,
            create_at=new_file.create_at,
            folder=folder_response
        )
    )



# API: Get document by id
@router.get("/document/{id}", response_model=APIResponse)
def get_document_by_id(id: int, current_user: TokenData = Depends(get_current_user), db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == id).first()

    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={"code": 1009, "message": "Document does not exist"})

    return APIResponse(
        code=1000,
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

# API: Delete document by id
@router.delete("/document/{id}")
def delete_document_by_id(id: int, current_user: TokenData = Depends(get_current_user), db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == id).first()

    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={"code": 1009, "message": "Document does not exist"})

    folder = db.query(Folder).filter(Folder.id == document.folder_id).first()
    if folder.author_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail={"code": 1007, "message": "You are not authorized to delete this document"})

    db.delete(document)
    db.commit()

    return {"message": "Document has been deleted"}


# API: Delete documents
@router.delete("/document")
def delete_list_documents(delete_list_documents_request: DeleteListDocumentsRequest,
                          current_user: TokenData = Depends(get_current_user),
                          db: Session = Depends(get_db)):
    document_ids = delete_list_documents_request.documents_id

    if len(document_ids) > 0:
        for doc_id in document_ids:
            document = db.query(Document).filter(Document.id == doc_id).first()
            if not document:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail={"code": 1009, "message": f"Document with id {doc_id} not found"})

            folder = db.query(Folder).filter(Folder.id == document.folder_id).first()
            if folder.author_id != current_user.user_id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                    detail={"code": 1007,
                                            "message": "You can't delete documents not in your own folder"})

            db.delete(document)

        db.commit()

    return APIResponse(
        code=1000,
        result=FileDeleteResponse(result="Delete successfully")
    )
