from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException
from sqlalchemy import func, and_
from datetime import datetime, timedelta

from app.models.boarding_house import BoardingHouse
from app.models.boarding_house_image import BoardingHouseImage
from app.models.review import Review
from app.schemas.boarding_house_schema import BoardingHouseCreate
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
