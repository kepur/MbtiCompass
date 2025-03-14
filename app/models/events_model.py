from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Enum, Float, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base
from enum import Enum as PyEnum
from .m2m_associations_model import event_participants
# 活动类型
class EventType(PyEnum):
    PRIVATE = "私人"
    PUBLIC = "公众"

# 活动状态
class EventStatus(PyEnum):
    PENDING = "待审核"
    CONFIRMED = "已确认"
    CANCELLED = "已取消"

# 支付方式
class PaymentType(PyEnum):
    AA = "AA"  # 参与者均摊
    SPONSOR = "主办方付费"
    FREE = "免费"
    CROWDFUNDING_ONLINE = "众筹线上"
    CROWDFUNDING_OFFLINE = "众筹线下"

# 活动兴趣申请状态
class InterestStatus(PyEnum):
    PENDING = "等待中"  # 等待发起人同意
    APPROVED = "已同意"  # 发起人已同意
    REJECTED = "已拒绝"  # 发起人已拒绝

# 活动兴趣申请
class EventInterest(Base):
    __tablename__ = "event_interests"
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)  # 关联活动
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 申请人
    status = Column(Enum(InterestStatus), default=InterestStatus.PENDING)  # 状态
    # 关系
    event = relationship("Event", back_populates="interested_users")
    user = relationship("User", back_populates="event_interests")

# 活动地点
class EventLocation(Base):
    __tablename__ = "event_locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)  # 位置名称，如 "Makati Zoo Café"
    latitude = Column(Float, nullable=False)  # 纬度
    longitude = Column(Float, nullable=False)  # 经度
    country = Column(String(100), nullable=True)  # 国家
    city = Column(String(100), nullable=True)  # 城市
    address = Column(String(1024), nullable=True)  # 详细地址
    # 关系
    events = relationship("Event", back_populates="location")

# 活动标签
class EventTag(Base):
    __tablename__ = "event_tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)  # 例如 "跑步", "喝咖啡"
    category = Column(String(255), nullable=False)  # "私人" or "公众"

    # 事件关联
    events = relationship("Event", secondary="event_tag_association", back_populates="tags")

# 多对多关系表（活动 & 标签）
event_tag_association = Table(
    "event_tag_association",
    Base.metadata,
    Column("event_id", Integer, ForeignKey("events.id")),
    Column("tag_id", Integer, ForeignKey("event_tags.id")),
)

# 活动表
class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)  # 活动标题
    description = Column(String(1024), nullable=True)  # 活动描述
    event_type = Column(Enum(EventType), nullable=False)  # 活动类型（私人/公众）
    category = Column(String(255), nullable=False)  # 具体活动分类（如约会、跑步、聚餐等）
    chat_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=True)  # 群聊 ID
    is_private_chat = Column(Boolean, default=False)  # 是否私人会话
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
    cancelled_reason = Column(String(1024), nullable=True)  # 取消原因


    # 关系字段
    organizer = relationship("User", back_populates="organized_events")
    participants = relationship("User", secondary=event_participants, back_populates="joined_events")

    tags = relationship("EventTag", secondary=event_tag_association, back_populates="events")
    location = relationship("EventLocation", back_populates="events")
    payment = relationship("EventPayment", back_populates="event", uselist=False)  # 一对一
    comments = relationship("Comment", back_populates="event")  # 活动的所有评论
    interested_users = relationship("EventInterest", back_populates="event")

    def check_participants(self):
        """ 检查人数是否达到要求，未达最小人数则取消 """
        if self.min_participants and self.current_participants < self.min_participants:
            self.status = EventStatus.CANCELLED
            self.cancelled_reason = "人数不足"

    def get_approved_participants(self):
        """ 获取已同意的参与者数量 """
        return len([interest for interest in self.interested_users if interest.status == InterestStatus.APPROVED])
