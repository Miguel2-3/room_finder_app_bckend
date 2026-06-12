from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException
from sqlalchemy import func, and_
from datetime import datetime, timedelta

from app.models.boarding_house import BoardingHouse
from app.models.boarding_house_image import BoardingHouseImage
from app.models.review import Review
from app.models.notification import Notification
from app.schemas.boarding_house_schema import BoardingHouseCreate, ReviewCreate
from app.models.user import User


#  CREATE
def create_boarding_house(
    db: Session,
    data: BoardingHouseCreate,
    owner_id: int
):
    #  STEP 1: Get user
    user = db.query(User).filter(User.id == owner_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    
    # LIMIT HERE
    count = db.query(BoardingHouse).filter(
        BoardingHouse.owner_id == owner_id
    ).count()

    if count >= 3:
        raise HTTPException(
            status_code=400,
            detail="You can only create up to 3 boarding houses"
        )

    #  STEP 2: Upgrade role
    if user.role != "landlord":
        user.role = "landlord"

    #  STEP 3: Create boarding house
    new_house = BoardingHouse(
        title=data.title,
        description=data.description,
        price=data.price,
        address=data.address,
        barangay=data.barangay,
        city=data.city,
        province=data.province,
        country=data.country,
        latitude=data.latitude,
        longitude=data.longitude,
        wifi_available=data.wifi_available,
        beds=data.beds,
        is_available=data.is_available,
        gender_allowed=data.gender_allowed,
        owner_id=owner_id
    )

    db.add(new_house)
    db.flush()  # Push to DB to get new_house.id without finishing the transaction

    # STEP 4: Save Images
    for img_url in data.images:
        db_image = BoardingHouseImage(house_id=new_house.id, image_url=img_url)
        db.add(db_image)
    
    db.commit()  # Single commit for role update, house creation, and images
    db.refresh(new_house)

    return translate_to_response(new_house)


def translate_to_response(house: BoardingHouse):
    """Helper to convert model to schema including images list"""
    house_dict = {c.name: getattr(house, c.name) for c in house.__table__.columns}
    house_dict["images"] = [img.image_url for img in house.images]
    house_dict["created_at"] = house.created_at
    house_dict["updated_at"] = house.updated_at
    return house_dict


# GET ALL + FILTER
def get_all_boarding_houses(
    db: Session,
    max_price: float | None = None,
    wifi: bool | None = None,
    barangay: str | None = None,
    city: str | None = None,
    province: str | None = None,
    skip: int = 0,
    limit: int = 20
):
    query = db.query(BoardingHouse).options(joinedload(BoardingHouse.images))

    # By default, only show available houses to the public
    query = query.filter(BoardingHouse.is_available == True)

    if max_price is not None:
        query = query.filter(BoardingHouse.price <= max_price)

    if wifi is not None:
        query = query.filter(BoardingHouse.wifi_available == wifi)

    if barangay:
        query = query.filter(BoardingHouse.barangay.ilike(f"%{barangay}%"))

    if city:
        query = query.filter(BoardingHouse.city.ilike(f"%{city}%"))

    if province:
        query = query.filter(BoardingHouse.province.ilike(f"%{province}%"))

    houses = query.offset(skip).limit(limit).all()
    return [translate_to_response(h) for h in houses]


# UPDATE
def update_boarding_house(
    db: Session,
    house_id: int,
    data: BoardingHouseCreate,
    user_id: int
):
    house = db.query(BoardingHouse).filter(BoardingHouse.id == house_id).first()

    if not house:
        return None

    if house.owner_id != user_id:
        return "unauthorized"

    #  UPDATE FIELDS
    house.title = data.title
    house.description = data.description
    house.price = data.price
    house.address = data.address
    house.barangay = data.barangay
    house.city = data.city
    house.province = data.province
    house.country = data.country
    house.latitude = data.latitude
    house.longitude = data.longitude
    house.wifi_available = data.wifi_available
    house.beds = data.beds
    house.is_available = data.is_available
    house.gender_allowed = data.gender_allowed

    # UPDATE IMAGES: Clear old ones and add new ones
    db.query(BoardingHouseImage).filter(BoardingHouseImage.house_id == house_id).delete()
    
    for img_url in data.images:
        db_image = BoardingHouseImage(house_id=house_id, image_url=img_url)
        db.add(db_image)

    db.commit()
    db.refresh(house)

    return translate_to_response(house)


#  DELETE
def delete_boarding_house(
    db: Session,
    house_id: int,
    user_id: int,
    confirmation_name: str
):
    house = db.query(BoardingHouse).filter(BoardingHouse.id == house_id).first()

    if not house:
        return None

    if house.owner_id != user_id:
        return "unauthorized"

    # Check if confirmation name matches (case-insensitive and trimmed)
    if house.title.strip().lower() != confirmation_name.strip().lower():
        return "name_mismatch"

    db.delete(house)
    db.commit()

    return True


def get_stale_boarding_houses(db: Session):
    """
    Finds boarding houses that haven't been updated in over 30 days.
    This can be used by a background task to send reminders.
    """
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    return db.query(BoardingHouse).filter(
        BoardingHouse.updated_at < thirty_days_ago
    ).all()


def process_update_reminders(db: Session):
    """
    Business logic to actually 'send' the reminders.
    """
    stale_houses = get_stale_boarding_houses(db)
    for house in stale_houses:
        # This is where you would integrate your notification service 
        # (e.g., Firebase Cloud Messaging or Email)
        print(f"NOTIFICATION: Sent reminder to Owner {house.owner_id} "
              f"for house '{house.title}' (Last updated: {house.updated_at})")
    return len(stale_houses)


#  GET SINGLE
def get_boarding_house_by_id(db: Session, house_id: int):
    house = db.query(BoardingHouse).options(joinedload(BoardingHouse.images)).filter(
        BoardingHouse.id == house_id
    ).first()
    if house:
        return translate_to_response(house)
    return None


#  GET MY OWN HOUSES
def get_my_boarding_houses(db: Session, owner_id: int):
    houses = db.query(BoardingHouse).filter(
        BoardingHouse.owner_id == owner_id
    ).all()
    return [translate_to_response(h) for h in houses]


# GET FEATURED HOUSES
def get_featured_boarding_houses(db: Session, limit: int = 5):
    """Fetches available houses marked as featured for the lively home screen."""
    houses = db.query(BoardingHouse).options(joinedload(BoardingHouse.images)).filter(
        BoardingHouse.is_available == True,
        BoardingHouse.is_featured == True
    ).limit(limit).all()
    return [translate_to_response(h) for h in houses]


# ADD REVIEW AND UPDATE RATING
def add_review(
    db: Session,
    house_id: int,
    user_id: int,
    review_data: ReviewCreate
):
    house = db.query(BoardingHouse).filter(BoardingHouse.id == house_id).first()
    if not house:
        raise HTTPException(status_code=404, detail="Boarding house not found")

    # 1. Create the new review
    new_review = Review(
        boarding_house_id=house_id,
        user_id=user_id,
        rating=review_data.rating,
        comment=review_data.comment
    )
    db.add(new_review)
    db.flush() # Flush to include the new review in our average calculation

    # 2. Calculate the new average rating
    avg_rating = db.query(func.avg(Review.rating)).filter(Review.boarding_house_id == house_id).scalar()
    if avg_rating is not None:
        house.rating = round(avg_rating, 1)

    db.commit()
    db.refresh(house)
    return translate_to_response(house)


# GET REVIEWS FOR HOUSE
def get_reviews_for_house(db: Session, house_id: int):
    return db.query(Review).filter(Review.boarding_house_id == house_id).order_by(Review.id.desc()).all()


# REPLY TO REVIEW
def reply_to_review(db: Session, review_id: int, owner_id: int, reply_text: str):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
        
    house = db.query(BoardingHouse).filter(BoardingHouse.id == review.boarding_house_id).first()
    if not house or house.owner_id != owner_id:
        raise HTTPException(status_code=403, detail="Only the landlord can reply to this review")
        
    review.reply = reply_text
    
    # Create an in-app notification for the tenant
    notification = Notification(
        user_id=review.user_id,
        title="Landlord Replied",
        message=f"The landlord replied to your review on '{house.title}'."
    )
    db.add(notification)
    
    db.commit()
    db.refresh(review)
    return review


# GET MY NOTIFICATIONS
def get_my_notifications(db: Session, user_id: int):
    return db.query(Notification).filter(Notification.user_id == user_id).order_by(Notification.created_at.desc()).all()

# MARK NOTIFICATION AS READ
def mark_notification_read(db: Session, notification_id: int, user_id: int):
    notif = db.query(Notification).filter(Notification.id == notification_id, Notification.user_id == user_id).first()
    if notif and not notif.is_read:
        notif.is_read = True
        db.commit()
