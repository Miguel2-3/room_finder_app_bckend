from sqlalchemy.orm import Session
from app.models.user import User

def update_user_profile(db: Session, user_id: int, name: str, phone: str):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.name = name
        user.phone = phone
        db.commit()
        db.refresh(user)
    return user