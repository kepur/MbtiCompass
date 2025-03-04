from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base
from enum import Enum as PyEnum

class CallStatus(PyEnum):
    ONGOING = "ongoing"  # 进行中
    ENDED = "ended"      # 已结束
    MISSED = "missed"    # 未接听

class CallSession(Base):
    __tablename__ = "call_sessions"

    id = Column(Integer, primary_key=True, index=True)
    caller_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    call_status = Column(Enum(CallStatus), default=CallStatus.ONGOING)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    is_video_call = Column(Boolean, default=True)  # 视频通话
    encryption_key = Column(String(255), nullable=False)  # 端到端加密密钥（仅存储哈希值）

    caller = relationship("User", foreign_keys=[caller_id])
    receiver = relationship("User", foreign_keys=[receiver_id])
