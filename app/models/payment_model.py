from sqlalchemy import Column, Integer, ForeignKey, Enum, Boolean, Float, DateTime, String
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base
from .enums_model import PaymentType
from enum import Enum as PyEnum

class EventPayment(Base):
    __tablename__ = "event_payments"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)  # 活动 ID
    payment_type = Column(Enum(PaymentType), nullable=False)  # 支付方式
    total_amount = Column(Float, nullable=True)  # 总金额（仅限众筹）
    paid_amount = Column(Float, default=0.0)  # 已支付金额（仅限众筹）
    is_fully_funded = Column(Boolean, default=False)  # 众筹是否完成
    payout_status = Column(Boolean, default=False)  # 是否已派发给发起人
    third_party_provider = Column(String, nullable=True)  # 第三方支付（GCash、Alipay）
    third_party_transaction_id = Column(String, nullable=True)  # 第三方支付交易 ID
    created_at = Column(DateTime, default=datetime.utcnow)  # 记录创建时间

    event = relationship("Event", back_populates="payment")
    contributors = relationship("CrowdfundingParticipants", back_populates="payment")

    def check_funding_status(self):
        """ 检查众筹是否达到目标金额 """
        if self.total_amount and self.paid_amount >= self.total_amount:
            self.is_fully_funded = True

# 定义支付状态枚举
class CrowdfundingStatus(PyEnum):
    PENDING = "pending"  # 待支付
    PAID = "paid"        # 已支付
    REFUNDED = "refunded"  # 已退款

class CrowdfundingParticipants(Base):
    __tablename__ = "crowdfunding_participants"

    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(Integer, ForeignKey("event_payments.id"), nullable=False)  # 关联支付记录
    contributor_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 参与者（用户）
    amount = Column(Float, nullable=False)  # 支付金额
    status = Column(Enum(CrowdfundingStatus), default=CrowdfundingStatus.PENDING)  # 支付状态
    paid_at = Column(DateTime, nullable=True)  # 支付时间
    created_at = Column(DateTime, default=datetime.utcnow)  # 记录创建时间

    # 关系
    payment = relationship("EventPayment", back_populates="contributors")
    contributor = relationship("User")

    def mark_as_paid(self):
        """ 标记为已支付 """
        self.status = CrowdfundingStatus.PAID
        self.paid_at = datetime.utcnow()

    def mark_as_refunded(self):
        """ 标记为已退款 """
        self.status = CrowdfundingStatus.REFUNDED