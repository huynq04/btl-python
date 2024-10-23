from datetime import datetime
from pydantic import BaseModel
from app.schemas.folder_schema import FolderResponse

class FileCreate(BaseModel):
    name: str
    firebase_id: str 

class FileResponse(BaseModel):
    id: int
    name: str
    create_at: datetime
    firebase_id: str

    folder: FolderResponse
