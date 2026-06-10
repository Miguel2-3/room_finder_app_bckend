from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.inquiry_schema import InquiryCreate
from app.services.inquiry_service import (
    create_inquiry,
    get_my_inquiries,
    get_inquiries_by_house,
    reply_to_inquiry,
    close_inquiry,
    get_owner_inquiries
)
from app.middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/inquiries", tags=["Inquiries"])


# Send inquiry (tenant)
@router.post("/")
def send_inquiry(
    data: InquiryCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return create_inquiry(db, data, current_user.id)


# View my inquiries (tenant)
@router.get("/my")
def my_inquiries(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return get_my_inquiries(db, current_user.id)


# View inquiries for a boarding house (landlord)
@router.get("/house/{boarding_house_id}")
def house_inquiries(
    boarding_house_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return get_inquiries_by_house(
        db,
        boarding_house_id,
        current_user.id
    )
# Owner replies to inquiry

@router.put("/{inquiry_id}/reply")
def reply_inquiry(
    inquiry_id: int,
    reply: str, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return reply_to_inquiry(
        db,
        inquiry_id,
        current_user.id,
        reply   # PASS IT
    )


# Owner closes inquiry

@router.put("/{inquiry_id}/close")
def close_inquiry_endpoint(
    inquiry_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return close_inquiry(db, inquiry_id, current_user.id)

@router.get("/owner")
def owner_inquiries(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return get_owner_inquiries(db, current_user.id)
