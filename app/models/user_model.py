from sqlalchemy import  Boolean, DateTime, ForeignKey, Text, Table
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Enum as SQLEnum
from datetime import datetime
from .base import Base
from .enums_model import ZodiacEnum,BaziEnum,MBTIEnum
from enum import Enum as PyEnum
from .m2m_associations_model import event_participants,chat_members


# 用户与标签的多对多关系表
User_Tags = Table(
    "user_tags",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)

class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    users = relationship("User", secondary=User_Tags, back_populates="tags")  # 反向关系


# 🔹 用户角色枚举
class UserRole(PyEnum):
    USER = "user"  # 普通用户
    ADMIN = "admin"  # 管理员


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=True)  # ✅ 允许邮箱为空，支持仅手机号注册
    phone_number = Column(String(50), unique=True, nullable=True)  # ✅ 手机号必须唯一
    hashed_password = Column(String(255), nullable=False)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    is_active = Column(Boolean, default=True)  # 是否活跃（注销时变为 False）

    # 📌 个人信息扩展
    username = Column(String(255), unique=True, nullable=False)
    birthdate = Column(DateTime, nullable=True)  # 生日
    gender = Column(String(255), nullable=True)  # 性别


    # 🔹 选择类型字段
    zodiac_sign = Column(SQLEnum(ZodiacEnum, native_enum=False), nullable=True)  # ✅
    mbti = Column(SQLEnum(MBTIEnum,native_enum=False), nullable=True)  # MBTI
    birth_date = Column(DateTime, nullable=True)  # 生日
    birth_time = Column(String(50), nullable=True)  # 出生时间（格式 14:30）
    lunar_birth_date = Column(String(20), nullable=True)  # 农历生日
    bazi = Column(String(50), nullable=True)  # 生辰八字（天干地支组合）
    wuxing = Column(String(20), nullable=True)  # 五行属性（木火土金水）

    # 关系字段
    favorite_music = Column(Text, nullable=True)  # 用户喜欢的音乐风格（逗号分隔）

    # 📌 关系
    # 与 ChatSession 的多对多关系
    posts = relationship("Post", back_populates="user")
    tags = relationship("Tag", secondary=User_Tags, back_populates="users")  # 用户自定义标签

    comments = relationship("Comment", back_populates="user")  # 用户的所有评论
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)  # 角色（默认为普通用户）
    # 与 Events 的关系
    organized_events = relationship("Event", back_populates="organizer")
    joined_events = relationship("Event", secondary=event_participants, back_populates="participants")
    # 与 ChatSession 的关系
    joined_chats = relationship("ChatSession", secondary=chat_members, back_populates="members")
    owned_chats = relationship("ChatSession", back_populates="owner")  # 群主拥有的群聊
    # 与 UserLocation 的关系（一对多）
    locations = relationship("UserLocation", back_populates="user")  # 改为复数，表示历史位置
    # 确保 event_interests 关系定义正确
    event_interests = relationship("EventInterest", back_populates="user")
    match_preferences = relationship("MatchPreference", back_populates="user", uselist=False)  # 一对一关系
    collections = relationship("MediaCollection", back_populates="user")


class BlockedUsers(Base):
    __tablename__ = "blocked_users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    blocked_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", foreign_keys=[user_id])
    blocked_user = relationship("User", foreign_keys=[blocked_user_id])

