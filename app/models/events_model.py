from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Enum, Float, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base
from enum import Enum as PyEnum


class EventType(PyEnum):
    PRIVATE = "私人"
    PUBLIC = "公众"

class EventStatus(PyEnum):
    PENDING = "待审核"
    CONFIRMED = "已确认"
    CANCELLED = "已取消"

class PaymentType(PyEnum):
    AA = "AA"  # 参与者均摊
    SPONSOR = "主办方付费"
    FREE = "免费"
    CROWDFUNDING_ONLINE = "众筹线上"
    CROWDFUNDING_OFFLINE = "众筹线下"

class InterestStatus(PyEnum):
    PENDING = "等待中"  # 等待发起人同意
    APPROVED = "已同意"  # 发起人已同意
    REJECTED = "已拒绝"  # 发起人已拒绝

class EventInterest(Base):
    __tablename__ = "event_interests"
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)  # 关联活动
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 申请人
    status = Column(Enum(InterestStatus), default=InterestStatus.PENDING)  # 状态
    # 关系
    event = relationship("Event", back_populates="interested_users")
    user = relationship("User", back_populates="event_interests")


class EventLocation(Base):
    __tablename__ = "event_locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # 位置名称，如 "Makati Zoo Café"
    latitude = Column(Float, nullable=False)  # 纬度
    longitude = Column(Float, nullable=False)  # 经度
    country = Column(String, nullable=True)  # 国家
    city = Column(String, nullable=True)  # 城市
    address = Column(String, nullable=True)  # 详细地址
    # 关系
    events = relationship("Event", back_populates="location")


# 多对多关系表（活动 & 标签）
event_tag_association = Table(
    "event_tag_association",
    Base.metadata,
    Column("event_id", Integer, ForeignKey("events.id")),
    Column("tag_id", Integer, ForeignKey("event_tags.id")),
)

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)  # 活动标题
    description = Column(String, nullable=True)  # 活动描述
    event_type = Column(Enum(EventType), nullable=False)  # 活动类型（私人/公众）
    category = Column(String, nullable=False)  # 具体活动分类（如约会、跑步、聚餐等）
    #创建活动自动生成群聊id
    chat_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=True)  # 群聊
    is_private_chat = Column(Boolean,default=False)  # 是否私人会话
    organizer_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 发起人
    start_time = Column(DateTime, nullable=False)  # 开始时间
    end_time = Column(DateTime, nullable=True)  # 结束时间
    max_participants = Column(Integer, nullable=False)  # 最大参与人数
    min_participants = Column(Integer, nullable=True)  # 最低参与人数（不满足自动取消）
    current_participants = Column(Integer, default=0)  # 当前报名人数
    average_budget = Column(Float, nullable=True)  # 预估人均预算
    status = Column(Enum(EventStatus), default=EventStatus.PENDING)  # 活动状态
    payment_type = Column(Enum(PaymentType), nullable=False)  # 支付方式（AA/主办方付费/免费/众筹）
    location_id = Column(Integer, ForeignKey("event_locations.id"))  # 位置 ID

    # 关系
    organizer = relationship("User", back_populates="events")
    tags = relationship("EventTag", secondary=event_tag_association, back_populates="events")
    location = relationship("EventLocation", back_populates="events")
    payment = relationship("EventPayment", back_populates="event", uselist=False)
    participants = relationship("EventParticipant", back_populates="event")
    interested_users = relationship("EventInterest", back_populates="event")
    cancelled_reason = Column(String, nullable=True)  # 取消原因
    comments = relationship("Comment", back_populates="event")  # 活动的所有评论

    def check_participants(self):
        """ 检查人数是否达到要求，未达最小人数则取消 """
        if self.min_participants and self.current_participants < self.min_participants:
            self.status = EventStatus.CANCELLED
            self.cancelled_reason = "人数不足"

    def get_approved_participants(self):
        """ 获取已同意的参与者数量 """
        return len([interest for interest in self.interested_users if interest.status == InterestStatus.APPROVED])
