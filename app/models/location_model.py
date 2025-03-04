from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class UserLocation(Base):
    __tablename__ = "user_locations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)  # 用户 ID
    latitude = Column(Float, nullable=False)  # 纬度
    longitude = Column(Float, nullable=False)  # 经度
    country = Column(String, nullable=True)  # 国家
    city = Column(String, nullable=True)  # 城市
    address = Column(String, nullable=True)  # 详细地址
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间

    # 关系
    user = relationship("User", back_populates="location")


class Business(Base):
    __tablename__ = "businesses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)  # cafe, bar, restaurant, etc.
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    rating = Column(Float, default=0.0)

