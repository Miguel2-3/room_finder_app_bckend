from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from app.core.database import Base


class Inquiry(Base):
    __tablename__ = "inquiries"

    # Primary key for the inquiry
    id = Column(Integer, primary_key=True, index=True)

    # The user who sends the inquiry (Tenant)
    tenant_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # The owner of the boarding house (Landlord)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # The boarding house being inquired about
    boarding_house_id = Column(Integer, ForeignKey("boarding_houses.id"), nullable=False)

    # Message sent by the tenant
    message = Column(String, nullable=False)

    # Reply from the landlord (optional at first)
    reply = Column(String, nullable=True)

    # Status of the inquiry:
    # "pending"  -> tenant sent message, waiting for reply
    # "replied"  -> landlord has replied
    # "closed"   -> conversation is closed
    status = Column(String, default="pending")

    # Flag to indicate if the inquiry is closed
    is_closed = Column(Boolean, default=False)