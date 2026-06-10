from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.middleware.auth_middleware import get_current_user
from app.models.user import User
from app.services import review_service
from pydantic import BaseModel

router = APIRouter(prefix="/reviews", tags=["Reviews"])

class ReviewCreate(BaseModel):
    boarding_house_id: int
    rating: int
    comment: str

@router.post("/")
def add_review(
    data: ReviewCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    return review_service.create_review(
        db, data.boarding_house_id, current_user.id, data.rating, data.comment
    )