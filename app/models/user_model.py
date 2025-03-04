from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Table
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Enum as SQLEnum
from datetime import datetime
from .base import Base
from .enums_model import ZodiacEnum,BaziEnum,MBTIEnum

# 用户与标签的多对多关系表
user_tags = Table(
    "user_tags",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 📌 个人信息扩展
    username = Column(String(255), unique=True, nullable=False)
    birthdate = Column(DateTime, nullable=True)  # 生日
    gender = Column(String(255), nullable=True)  # 性别


    # 🔹 选择类型字段
    zodiac_sign = Column(SQLEnum(ZodiacEnum, native_enum=False), nullable=True)  # ✅
    mbti = Column(SQLEnum(MBTIEnum,native_enum=False), nullable=True)  # MBTI
    birth_date = Column(DateTime, nullable=False)  # 生日
    birth_time = Column(String(50), nullable=True)  # 出生时间（格式 14:30）
    lunar_birth_date = Column(String(20), nullable=True)  # 农历生日
    bazi = Column(String(50), nullable=True)  # 生辰八字（天干地支组合）
    wuxing = Column(String(20), nullable=True)  # 五行属性（木火土金水）

    # 关系字段
    activities = relationship("Activity", back_populates="user")
    favorite_music = Column(Text, nullable=True)  # 用户喜欢的音乐风格（逗号分隔）

    # 📌 关系
    chats = relationship("Chat", back_populates="user")
    posts = relationship("Post", back_populates="user")
    tags = relationship("Tag", secondary=user_tags, back_populates="users")  # 用户自定义标签

    comments = relationship("Comment", back_populates="user")  # 用户的所有评论


class BlockedUsers(Base):
    __tablename__ = "blocked_users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    blocked_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", foreign_keys=[user_id])
    blocked_user = relationship("User", foreign_keys=[blocked_user_id])

