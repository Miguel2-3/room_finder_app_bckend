from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class BoardingHouseImage(Base):
    __tablename__ = "boarding_house_images"

    id = Column(Integer, primary_key=True, index=True)
    house_id = Column(Integer, ForeignKey("boarding_houses.id"))
    image_url = Column(String, nullable=False)

    boarding_house = relationship("BoardingHouse", back_populates="images")