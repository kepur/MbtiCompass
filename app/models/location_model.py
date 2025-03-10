from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class UserLocation(Base):
    __tablename__ = "user_locations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 用户 ID
    latitude = Column(Float, nullable=False)  # 纬度
    longitude = Column(Float, nullable=False)  # 经度
    country = Column(String(100), nullable=True)  # ✅ 修正：加上长度
    city = Column(String(100), nullable=True)  # ✅ 修正：加上长度
    address = Column(String(255), nullable=True)  # ✅ 修正：加上长度
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)  # 更新时间

    # 关系
    user = relationship("User", back_populates="locations")  # 改为复数 "locations"
    posts = relationship("Post", back_populates="location")  # 一个位置多个帖子
class Business(Base):
    __tablename__ = "businesses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)  # ✅ 修正：加上长度
    category = Column(String(100), nullable=False)  # ✅ 修正：加上长度
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    rating = Column(Float, nullable=True)  # ✅ 允许 NULL，避免 0.0 误导用户
