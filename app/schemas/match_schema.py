from pydantic import BaseModel
from typing import Optional
from app.models.enums_model import ZodiacEnum, MBTIEnum, EducationEnum

class MatchPreferenceCreate(BaseModel):
    min_age: int = 18
    max_age: int = 40
    zodiac_preference: Optional[ZodiacEnum]
    mbti_preference: Optional[MBTIEnum]
    education_preference: Optional[EducationEnum]

class MatchPreferenceResponse(MatchPreferenceCreate):
    id: int
    user_id: int

    class Config:
        orm_mode = True
