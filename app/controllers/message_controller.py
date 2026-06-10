from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.middleware.auth_middleware import get_current_user
from app.schemas.message_schema import MessageCreate, MessageResponse
from app.services.message_service import send_chat_message, get_chat_history

router = APIRouter(prefix="/messages", tags=["Messages"])

@router.post("/", response_model=MessageResponse)
def send_message(data: MessageCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return send_chat_message(db, data, current_user.id)

@router.get("/{inquiry_id}", response_model=list[MessageResponse])
def get_messages(inquiry_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return get_chat_history(db, inquiry_id, current_user.id)