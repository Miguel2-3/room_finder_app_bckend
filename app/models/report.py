from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    
    # The user who is making the report
    reporter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Type of thing being reported: 'boarding_house', 'review', or 'user'
    target_type = Column(String, nullable=False)
    
    # The ID of the thing being reported
    target_id = Column(Integer, nullable=False)
    
    # Why they are reporting it
    reason = Column(String, nullable=False)
    description = Column(String, nullable=True)
    
    # Status for admin review: 'pending', 'reviewed', 'resolved', 'dismissed'
    status = Column(String, default="pending")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
