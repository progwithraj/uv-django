from pydantic import BaseModel
from typing import Optional

class UserDetailsResponse(BaseModel):
    message: Optional[str] = None
    data: Optional[object] = None
    error: Optional[str] = None
