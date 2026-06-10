from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class BoardingHouseCreate(BaseModel):
    title: str
    description: str | None = None
    price: float
    address: str
    barangay: str | None = None
    city: str | None = None
    province: str | None = None
    country: str = "Philippines"

    latitude: float | None = None
    longitude: float | None = None

    wifi_available: bool = False
    beds: int = 1
    gender_allowed: str | None = None
    is_available: bool = True
    is_featured: bool = False

    # Image URLs from Supabase (Min 2, Max 8)
    images: list[str] = Field(..., min_length=2, max_length=8)


class BoardingHouseResponse(BaseModel):
    id: int
    title: str
    description: str | None
    price: float
    address: str
    barangay: str | None
    city: str | None
    province: str | None
    country: str
    latitude: float | None
    longitude: float | None
    wifi_available: bool
    beds: int
    gender_allowed: str | None
    is_available: bool
    is_featured: bool
    images: Optional[list[str]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True