from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ReportBase(BaseModel):
    target_type: str  # 'boarding_house', 'review', or 'user'
    target_id: int
    reason: str
    description: Optional[str] = None

class ReportCreate(ReportBase):
    pass

class ReportUpdate(BaseModel):
    status: str  # 'reviewed', 'resolved', 'dismissed'

class ReportResponse(ReportBase):
    id: int
    reporter_id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
