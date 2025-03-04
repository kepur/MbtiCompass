from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from .base import Base
from enum import Enum as PyEnum


# 定义消息类型枚举
class MessageType(PyEnum):
    TEXT = "text"       # 文本消息
    IMAGE = "image"     # 图片消息
    VIDEO = "video"     # 视频消息
    VOICE = "voice"     # 语音消息


class PrivateMessage(Base):
    """ 私聊消息表 """
    __tablename__ = "private_messages"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 发送者
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 接收者
    message_type = Column(Enum(MessageType), nullable=False)  # 消息类型
    content = Column(String, nullable=True)  # 文字内容
    media_url = Column(String, nullable=True)  # 语音/视频/图片的URL
    encrypted_message = Column(String, nullable=True)  # 加密的文本
    is_read = Column(Boolean, default=False)  # 是否已读
    is_deleted = Column(Boolean, default=False)  # 是否已删除
    is_self_destruct = Column(Boolean, default=False)  # 阅后即焚
    self_destruct_after = Column(Integer, nullable=True)  # 阅后即焚秒数
    is_recalled = Column(Boolean, default=False)  # 是否撤回
    created_at = Column(DateTime, default=datetime.utcnow)  # 发送时间
    expires_at = Column(DateTime, nullable=True)  # 阅后即焚时间

    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])

    def set_self_destruct(self, seconds: int):
        """ 设置阅后即焚 """
        self.is_self_destruct = True
        self.self_destruct_after = seconds
        self.expires_at = datetime.utcnow() + timedelta(seconds=seconds)

    def recall_message(self):
        """ 撤回消息 """
        self.is_recalled = True
        self.content = "[消息已撤回]"
        self.media_url = None
        self.encrypted_message = None


class GroupMessage(Base):
    """ 群聊消息表 """
    __tablename__ = "group_messages"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 发送者
    chat_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)  # 群聊会话ID
    message_type = Column(Enum(MessageType), nullable=False)  # 消息类型
    content = Column(String, nullable=True)  # 文字内容
    media_url = Column(String, nullable=True)  # 语音/视频/图片的URL
    encrypted_message = Column(String, nullable=True)  # 加密的文本
    is_deleted = Column(Boolean, default=False)  # 是否已删除
    is_self_destruct = Column(Boolean, default=False)  # 阅后即焚
    self_destruct_after = Column(Integer, nullable=True)  # 阅后即焚秒数
    is_recalled = Column(Boolean, default=False)  # 是否撤回
    created_at = Column(DateTime, default=datetime.utcnow)  # 发送时间
    expires_at = Column(DateTime, nullable=True)  # 阅后即焚时间

    sender = relationship("User", foreign_keys=[sender_id])
    chat = relationship("ChatSession", foreign_keys=[chat_id])

    def set_self_destruct(self, seconds: int):
        """ 设置阅后即焚 """
        self.is_self_destruct = True
        self.self_destruct_after = seconds
        self.expires_at = datetime.utcnow() + timedelta(seconds=seconds)

    def recall_message(self):
        """ 撤回消息 """
        self.is_recalled = True
        self.content = "[消息已撤回]"
        self.media_url = None
        self.encrypted_message = None


class ChatSession(Base):
    """ 群聊会话表 """
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # 群名称
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 群主
    created_at = Column(DateTime, default=datetime.utcnow)  # 创建时间

    owner = relationship("User", foreign_keys=[owner_id])
    members = relationship("ChatMember", back_populates="chat")


class ChatMember(Base):
    """ 群成员表 """
    __tablename__ = "chat_members"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow)

    chat = relationship("ChatSession", back_populates="members")
    user = relationship("User", foreign_keys=[user_id])
