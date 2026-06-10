from pydantic import BaseModel


class ReviewCreate(BaseModel):
    rating: int
    comment: str | None = None
    boarding_house_id: int

class ReviewUpdate(BaseModel):
    rating: int
    comment: str | None = None

class ReviewResponse(BaseModel):
    id: int
    rating: int
    comment: str | None
    user_id: int

    class Config:
        from_attributes = True
