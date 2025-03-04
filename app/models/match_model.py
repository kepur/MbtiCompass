from sqlalchemy import Column, Integer, ForeignKey, Enum, Float, Text
from sqlalchemy.orm import relationship
from .base import Base
from .enums_model import ZodiacEnum, EducationEnum, GenderEnum


class MatchPreference(Base):
    """
    该表存储用户的匹配偏好设定，用于个性化推荐。
    """
    __tablename__ = "match_preferences"

    id = Column(Integer, primary_key=True, index=True)  # 主键 ID
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 关联的用户 ID
    min_age = Column(Integer, nullable=True, default=18)  # 允许的最小年龄，默认为 18 岁
    max_age = Column(Integer, nullable=True, default=40)  # 允许的最大年龄，默认为 40 岁
    gender = Column(Enum(GenderEnum), nullable=True)  # 期望匹配的性别，可为空
    education_preference = Column(Enum(EducationEnum), nullable=True)  # 期望的学历要求，可为空
    preferred_hobbies = Column(Text, nullable=True)  # 用户偏好的兴趣爱好，以文本形式存储
    max_distance = Column(Float, nullable=True)  # 允许的最大距离（单位：公里），可为空

    # 关系绑定
    user = relationship("User", back_populates="match_preferences")  # 绑定到 User 表，形成一对一关系