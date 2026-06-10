from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.user_schema import UserResponse
from app.models.user import User
from app.core.database import get_db
from app.middleware.auth_middleware import get_current_user

router = APIRouter()


# PROFILE (Protected)
@router.get("/users/profile", response_model=UserResponse)
def get_profile(current_user = Depends(get_current_user)):
    return current_user