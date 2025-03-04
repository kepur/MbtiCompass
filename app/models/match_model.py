from sqlalchemy import Column, Integer, ForeignKey, Enum,Float,Text
from sqlalchemy.orm import relationship
from .base import Base
from .enums_model import ZodiacEnum, EducationEnum,GenderEnum

class MatchPreference(Base):
    __tablename__ = "match_preferences"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    min_age = Column(Integer, nullable=True, default=18)
    max_age = Column(Integer, nullable=True, default=40)
    gender = Column(Enum(GenderEnum), nullable=True)
    education_preference = Column(Enum(EducationEnum), nullable=True)
    preferred_hobbies = Column(Text, nullable=True)  # 喜欢的兴趣
    max_distance = Column(Float, nullable=True)      # 最大距离（公里）
    user = relationship("User", back_populates="match_preferences")