from sqlalchemy import Column, Integer, ForeignKey, Enum, Boolean, Float, DateTime, String
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base
from .enums_model import PaymentType
from enum import Enum as PyEnum

class EventPayment(Base):
    """ 活动支付表：存储活动的支付信息，如众筹支付情况 """
    __tablename__ = "event_payments"

    id = Column(Integer, primary_key=True, index=True)  # 主键 ID
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)  # 关联的活动 ID
    payment_type = Column(Enum(PaymentType), nullable=False)  # 支付方式（枚举值）
    total_amount = Column(Float, nullable=True)  # 众筹目标总金额（可为空，适用于非众筹支付）
    paid_amount = Column(Float, default=0.0)  # 当前已支付金额
    is_fully_funded = Column(Boolean, default=False)  # 是否众筹完成
    payout_status = Column(Boolean, default=False)  # 众筹资金是否已支付给发起人
    third_party_provider = Column(String(50), nullable=True)  # 第三方支付平台（如 GCash、Alipay）
    third_party_transaction_id = Column(String(100), nullable=True)  # 第三方支付交易 ID
    created_at = Column(DateTime, default=datetime.utcnow)  # 记录创建时间

    # 关系
    event = relationship("Event", back_populates="payment")  # 关联活动表
    contributors = relationship("CrowdfundingParticipants", back_populates="payment")  # 关联众筹参与者

    def check_funding_status(self):
        """ 检查当前众筹是否已达到目标金额 """
        if self.total_amount and self.paid_amount >= self.total_amount:
            self.is_fully_funded = True

# 定义众筹支付状态枚举
class CrowdfundingStatus(PyEnum):
    """ 众筹支付状态 """
    PENDING = "pending"  # 待支付
    PAID = "paid"  # 已支付
    REFUNDED = "refunded"  # 已退款

class CrowdfundingParticipants(Base):
    """ 众筹参与者表：记录用户的众筹支付信息 """
    __tablename__ = "crowdfunding_participants"

    id = Column(Integer, primary_key=True, index=True)  # 主键 ID
    payment_id = Column(Integer, ForeignKey("event_payments.id"), nullable=False)  # 关联支付记录 ID
    contributor_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 参与者用户 ID
    amount = Column(Float, nullable=False)  # 支付金额
    status = Column(Enum(CrowdfundingStatus), default=CrowdfundingStatus.PENDING)  # 当前支付状态
    paid_at = Column(DateTime, nullable=True)  # 付款时间（若已支付）
    created_at = Column(DateTime, default=datetime.utcnow)  # 记录创建时间

    # 关系
    payment = relationship("EventPayment", back_populates="contributors")  # 关联支付记录
    contributor = relationship("User")  # 关联用户

    def mark_as_paid(self):
        """ 标记当前支付记录为已支付，并记录支付时间 """
        self.status = CrowdfundingStatus.PAID
        self.paid_at = datetime.utcnow()

    def mark_as_refunded(self):
        """ 标记当前支付记录为已退款 """
        self.status = CrowdfundingStatus.REFUNDED
