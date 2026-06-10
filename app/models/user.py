from sqlalchemy import Column, Integer, String, Boolean
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)

    phone = Column(String, nullable=True)

    role = Column(String, default="tenant")

    email_verified = Column(Boolean, default=False)
    phone_verified = Column(Boolean, default=False)

    verification_status = Column(String, default="pending")

    is_active = Column(Boolean, default=True)