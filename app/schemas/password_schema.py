from pydantic import BaseModel, Field

class ChangePassWordRequest(BaseModel):
    old_password: str
    new_password: str= Field(..., min_length=8, description="Password must be at least 8 characters")