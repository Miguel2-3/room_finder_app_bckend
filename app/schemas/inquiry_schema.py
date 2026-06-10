from pydantic import BaseModel

class InquiryCreate(BaseModel):
    boarding_house_id: int
    message: str