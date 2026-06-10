from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.middleware.auth_middleware import get_current_user
from app.models.favorite import Favorite

router = APIRouter(prefix="/favorites", tags=["Favorites"])


# ✅ TOGGLE FAVORITE
@router.post("/{property_id}")
def toggle_favorite(
    property_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    try:
        existing = db.query(Favorite).filter(
            Favorite.user_id == current_user.id,
            Favorite.property_id == property_id
        ).first()

        if existing:
            db.delete(existing)
            db.commit()
            return {
                "message": "Removed from favorites",
                "is_favorited": False
            }

        new_favorite = Favorite(
            user_id=current_user.id,
            property_id=property_id
        )

        db.add(new_favorite)
        db.commit()

        return {
            "message": "Added to favorites",
            "is_favorited": True
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ✅ GET ALL FAVORITES OF CURRENT USER
@router.get("/")
def get_my_favorites(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    favorites = db.query(Favorite).filter(
        Favorite.user_id == current_user.id
    ).all()

    return [
        {
            "property_id": f.property_id,
            "created_at": f.created_at
        }
        for f in favorites
    ]


# ✅ CHECK IF SINGLE PROPERTY IS FAVORITED (IMPORTANT FOR UI LOAD)
@router.get("/check/{property_id}")
def check_favorite(
    property_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    exists = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.property_id == property_id
    ).first()

    return {
        "property_id": property_id,
        "is_favorited": exists is not None
    }