from sqlalchemy import Column, Integer, String, ForeignKey
from app.core.database import Base


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)

    rating = Column(Integer, nullable=False)  # 1–5
    comment = Column(String, nullable=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    boarding_house_id = Column(Integer, ForeignKey("boarding_houses.id"), nullable=False)
