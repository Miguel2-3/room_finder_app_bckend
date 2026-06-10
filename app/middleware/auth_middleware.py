from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.utils.supabase_auth import verify_token

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    #  Check missing token
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing token"
        )

    #  Verify Supabase token
    payload = verify_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    #  Extract email
    email = payload.get("email")

    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    #  STRICT CHECK — must be verified
    email_verified = payload.get("email_confirmed_at") is not None

    if not email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified"
        )

    #  Extract name safely
    name = payload.get("user_metadata", {}).get("name", "New User")

    #  Check if user exists
    user = db.query(User).filter(User.email == email).first()

    # Create ONLY verified users
    if not user:
        user = User(
            email=email,
            name=name,
            password="supabase_auth",
            role="tenant",
            email_verified=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    elif not user.email_verified:
        user.email_verified = True
        db.commit()
        db.refresh(user)

    return user