from typing import Optional, Any

from pydantic import BaseModel


class APIResponse(BaseModel):
    code: int
    result: Optional[Any] = None
    message: Optional[str] = None
    error_message: Optional[str] = None