from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 评论者
    content = Column(String(255), nullable=False)  # 评论内容
    created_at = Column(DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间
    is_deleted = Column(Boolean, default=False)  # 是否被删除
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True)  # 父评论 ID，支持嵌套回复
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=True)  # 关联帖子（可选）
    event_id = Column(Integer, ForeignKey("events.id"), nullable=True)  # 关联活动（可选）

    # 关系
    user = relationship("User", back_populates="comments")  # 评论者
    post = relationship("Post", back_populates="comments")  # 关联的帖子
    event = relationship("Event", back_populates="comments")  # 关联的活动
    parent = relationship("Comment", remote_side=[id], back_populates="replies")  # 父评论
    replies = relationship("Comment", back_populates="parent")  # 子评论（回复）

    def soft_delete(self):
        """ 软删除评论 """
        self.is_deleted = True
        self.content = "[评论已删除]"

class CommentLike(Base):
    __tablename__ = "comment_likes"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    comment_id = Column(Integer, ForeignKey("comments.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User")
    comment = relationship("Comment")
