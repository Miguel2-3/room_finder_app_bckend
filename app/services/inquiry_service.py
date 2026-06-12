from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.inquiry import Inquiry
from app.models.message import Message
from app.models.boarding_house import BoardingHouse

def get_my_inquiries(db: Session, user_id: int):
    # 1. Fetch the user's inquiries (either as a tenant or the landlord)
    inquiries = db.query(Inquiry).join(BoardingHouse).filter(
        (Inquiry.tenant_id == user_id) | (BoardingHouse.owner_id == user_id)
    ).all()

    results = []
    for inquiry in inquiries:
        # 2. Count unread messages for this specific inquiry thread
        # We only count messages sent by the OTHER person
        unread_count = db.query(func.count(Message.id)).filter(
            Message.inquiry_id == inquiry.id,
            Message.sender_id != user_id,
            Message.is_read == False
        ).scalar() or 0

        # 3. Add the unread_count to your inquiry response dictionary
        inquiry_data = {
            "id": inquiry.id,
            "tenant_id": inquiry.tenant_id,
            "boarding_house_id": inquiry.boarding_house_id,
            "status": inquiry.status,
            "message": inquiry.message,
            "reply": inquiry.reply,
            "created_at": inquiry.created_at.isoformat() if inquiry.created_at else None,
            "updated_at": inquiry.updated_at.isoformat() if inquiry.updated_at else None,
            "unread_count": unread_count, # <-- Add the calculated count here
            "boarding_house": {
                "id": inquiry.boarding_house.id,
                "title": inquiry.boarding_house.title,
                # ... include any other boarding house fields your frontend expects
            }
        }
        results.append(inquiry_data)

    return results
