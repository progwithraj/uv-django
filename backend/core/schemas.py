from ninja import Schema
from typing import Optional
class IndexSchema(Schema):
    val: str
    val2: Optional[str] = None
    
class IndexResponse(Schema):
    message: str
    data: Optional[str] = None
