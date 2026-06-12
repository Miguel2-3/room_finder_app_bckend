from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class BoardingHouse(Base):
    __tablename__ = "boarding_houses"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String, nullable=False)
    description = Column(String, nullable=True)

    price = Column(Float, nullable=False)

    address = Column(String, nullable=False)
    barangay = Column(String, nullable=True)
    city = Column(String, nullable=True)
    province = Column(String, nullable=True)
    country = Column(String, default="Philippines")
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    wifi_available = Column(Boolean, default=False)
    beds = Column(Integer, default=1)

    gender_allowed = Column(String, nullable=True)
    
    is_available = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    rating = Column(Float, default=0.0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    images = relationship("BoardingHouseImage", back_populates="boarding_house", cascade="all, delete-orphan")
