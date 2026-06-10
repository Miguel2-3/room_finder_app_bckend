from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.message import Message
from app.models.inquiry import Inquiry
from app.models.boarding_house import BoardingHouse
from app.schemas.message_schema import MessageCreate

def send_chat_message(db: Session, data: MessageCreate, sender_id: int):
    # Verify inquiry chat room exists
    inquiry = db.query(Inquiry).filter(Inquiry.id == data.inquiry_id).first()
    if not inquiry:
        raise HTTPException(status_code=404, detail="Inquiry session not found")
    
    # Verify sender is either the tenant or the boarding house owner
    house = db.query(BoardingHouse).filter(BoardingHouse.id == inquiry.boarding_house_id).first()
    if sender_id != inquiry.tenant_id and sender_id != house.owner_id:
        raise HTTPException(status_code=403, detail="Not authorized to message in this thread")

    new_msg = Message(
        inquiry_id=data.inquiry_id,
        sender_id=sender_id,
        content=data.content
    )
    
    # Automatically update status to 'replied' if landlord sends it
    if sender_id == house.owner_id and inquiry.status == "pending":
        inquiry.status = "replied"

    db.add(new_msg)
    db.commit()
    db.refresh(new_msg)
    return new_msg

def get_chat_history(db: Session, inquiry_id: int, user_id: int):
    inquiry = db.query(Inquiry).filter(Inquiry.id == inquiry_id).first()
    if not inquiry:
        raise HTTPException(status_code=404, detail="Inquiry session not found")

    house = db.query(BoardingHouse).filter(BoardingHouse.id == inquiry.boarding_house_id).first()
    if user_id != inquiry.tenant_id and user_id != house.owner_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Mark incoming messages as read
    db.query(Message).filter(Message.inquiry_id == inquiry_id, Message.sender_id != user_id).update({"is_read": True})
    db.commit()

    return db.query(Message).filter(Message.inquiry_id == inquiry_id).order_by(Message.timestamp.asc()).all()