from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.review import Review
from app.models.boarding_house import BoardingHouse

def create_review(db: Session, boarding_house_id: int, user_id: int, rating: int, comment: str):
    # 1. Verify house exists
    house = db.query(BoardingHouse).filter(BoardingHouse.id == boarding_house_id).first()
    if not house:
        raise HTTPException(status_code=404, detail="Boarding House not found")

    # 2. Enforce Ownership Rule: Owner cannot review their own house
    if house.owner_id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot leave a review for your own property."
        )

    new_review = Review(
        rating=rating,
        comment=comment,
        user_id=user_id,
        boarding_house_id=boarding_house_id
    )
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_review