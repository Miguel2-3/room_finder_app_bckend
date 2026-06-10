from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)

    # Supabase user ID (UUID string)
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    #  Connected to boarding houses
    property_id = Column(
        Integer,
        ForeignKey("boarding_houses.id"),
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # Prevent duplicate favorites
    __table_args__ = (
        UniqueConstraint("user_id", "property_id"),
    )

    # Relationships
    user = relationship("User")
    property = relationship("BoardingHouse")