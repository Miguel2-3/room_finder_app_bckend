from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.models.inquiry import Inquiry
from app.models.boarding_house import BoardingHouse
from app.schemas.inquiry_schema import InquiryCreate


# Create a new inquiry from tenant to landlord
def create_inquiry(db: Session, data: InquiryCreate, user_id: int):

    # Get the boarding house to know who owns it
    house = db.query(BoardingHouse).filter(
        BoardingHouse.id == data.boarding_house_id
    ).first()

    if not house:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Boarding house not found"
        )

    # Prevent user from sending inquiry to their own house
    if house.owner_id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot inquire your own property"
        )

    inquiry = Inquiry(
        tenant_id=user_id,
        owner_id=house.owner_id,
        boarding_house_id=data.boarding_house_id,
        message=data.message
    )

    db.add(inquiry)

    try:
        db.commit()
        db.refresh(inquiry)
        return inquiry

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You already sent an inquiry for this boarding house"
        )


# Tenant views their own inquiries
def get_my_inquiries(db: Session, user_id: int):
    return db.query(Inquiry).filter(
        Inquiry.tenant_id == user_id
    ).all()


# Owner views inquiries for a specific house
def get_inquiries_by_house(db: Session, boarding_house_id: int, current_user_id: int):

    house = db.query(BoardingHouse).filter(
        BoardingHouse.id == boarding_house_id
    ).first()

    if not house:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Boarding house not found"
        )

    # Only the owner of the house can view its inquiries
    if house.owner_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to view these inquiries"
        )

    return db.query(Inquiry).filter(
        Inquiry.boarding_house_id == boarding_house_id
    ).all()


# Owner replies to an inquiry
def reply_to_inquiry(db: Session, inquiry_id: int, current_user_id: int, reply_text: str):

    inquiry = db.query(Inquiry).filter(
        Inquiry.id == inquiry_id
    ).first()

    if not inquiry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inquiry not found"
        )

    # Only the owner can reply
    if inquiry.owner_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to reply to this inquiry"
        )

    # Prevent replying to closed inquiry
    if inquiry.is_closed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inquiry is already closed"
        )
    # Prevent empty reply
    if not reply_text.strip():
        raise HTTPException(
            status_code=400,
            detail="Reply cannot be empty"
        )

    inquiry.reply = reply_text
    inquiry.status = "replied"

    db.commit()
    db.refresh(inquiry)

    return inquiry


# Owner closes an inquiry
def close_inquiry(db: Session, inquiry_id: int, current_user_id: int):

    inquiry = db.query(Inquiry).filter(
        Inquiry.id == inquiry_id
    ).first()

    if not inquiry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inquiry not found"
        )

    # Only owner can close
    if inquiry.owner_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to close this inquiry"
        )

    # Prevent closing twice
    if inquiry.is_closed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inquiry already closed"
        )

    inquiry.status = "closed"
    inquiry.is_closed = True

    db.commit()
    db.refresh(inquiry)

    return {"message": "Inquiry closed successfully"}


# Owner views all inquiries across all owned houses
def get_owner_inquiries(db: Session, owner_id: int):
    return db.query(Inquiry).filter(
        Inquiry.owner_id == owner_id
    ).all()