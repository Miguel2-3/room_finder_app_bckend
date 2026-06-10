import requests
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer
from app.core.config import settings

security = HTTPBearer()

def verify_token(token: str):
    url = f"{settings.SUPABASE_URL}/auth/v1/user"

    headers = {
        "Authorization": f"Bearer {token}",
        "apikey": settings.SUPABASE_ANON_KEY
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    return response.json()

def get_current_user(credentials = Depends(security)):
    token = credentials.credentials
    return verify_token(token)