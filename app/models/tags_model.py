from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .base import Base
from .user_model import user_tags

class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    users = relationship("User", secondary=user_tags, back_populates="tags")  # 反向关系
