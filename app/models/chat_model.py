# chat_model.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime,timedelta
from .base import Base
from .m2m_associations_model import chat_members
from enum import Enum as PyEnum


# 定义消息类型枚举（保持不变）
class MessageType(PyEnum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    VOICE = "voice"

# 定义群聊状态枚举
class ChatStatus(PyEnum):
    ACTIVE = "active"      # 活跃
    DISSOLVED = "dissolved"  # 已解散

class ChatSession(Base):
    """ 群聊会话表 """
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)  # 群名称
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 群主
    created_at = Column(DateTime, default=datetime.now)  # 创建时间
    status = Column(Enum(ChatStatus), default=ChatStatus.ACTIVE, nullable=False)  # 群聊状态

    # 关系
    owner = relationship("User", back_populates="owned_chats")  # 群主
    members = relationship("User", secondary=chat_members, back_populates="joined_chats")  # 成员

    def dissolve(self, user_id: int):
        """ 解散群组，仅限群主操作 """
        if self.owner_id != user_id:
            raise ValueError("只有群主可以解散群组")
        self.status = ChatStatus.DISSOLVED
        # 可选：清空成员（需要数据库支持）
        # self.members.clear()  # 如果需要清空成员列表，需在业务逻辑中处理

class GroupMessage(Base):
    """ 群聊消息表 """
    __tablename__ = "group_messages"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    chat_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    message_type = Column(Enum(MessageType), nullable=False)
    content = Column(String(255), nullable=True)
    media_url = Column(String(255), nullable=True)
    encrypted_message = Column(String(255), nullable=True)
    is_deleted = Column(Boolean, default=False)
    is_self_destruct = Column(Boolean, default=False)
    self_destruct_after = Column(Integer, nullable=True)
    is_recalled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    expires_at = Column(DateTime, nullable=True)

    sender = relationship("User", foreign_keys=[sender_id])
    chat = relationship("ChatSession", foreign_keys=[chat_id])

    def set_self_destruct(self, seconds: int):
        self.is_self_destruct = True
        self.self_destruct_after = seconds
        self.expires_at = datetime.now() + timedelta(seconds=seconds)

    def recall_message(self):
        self.is_recalled = True
        self.content = "[消息已撤回]"
        self.media_url = None
        self.encrypted_message = None



class PrivateMessage(Base):
    """ 私聊消息表 """
    __tablename__ = "private_messages"
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message_type = Column(Enum(MessageType), nullable=False)
    content = Column(String(255), nullable=True)
    media_url = Column(String(255), nullable=True)
    encrypted_message = Column(String(255), nullable=True)
    is_read = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    is_self_destruct = Column(Boolean, default=False)
    self_destruct_after = Column(Integer, nullable=True)
    is_recalled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    expires_at = Column(DateTime, nullable=True)

    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])

    def set_self_destruct(self, seconds: int):
        self.is_self_destruct = True
        self.self_destruct_after = seconds
        self.expires_at = datetime.now() + timedelta(seconds=seconds)

    def recall_message(self):
        self.is_recalled = True
        self.content = "[消息已撤回]"
        self.media_url = None
        self.encrypted_message = None