from pydantic import BaseModel
from datetime import datetime

class MessageCreate(BaseModel):
    inquiry_id: int
    content: str

class MessageResponse(BaseModel):
    id: int
    inquiry_id: int
    sender_id: int
    content: str
    timestamp: datetime
    is_read: bool

    class Config:
        from_attributes = True