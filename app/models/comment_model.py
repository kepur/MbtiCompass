from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 关联用户 ID
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=True)  # 关联帖子 ID
    event_id = Column(Integer, ForeignKey("events.id"), nullable=True)  # 关联活动 ID（可选）
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True)  # 父评论 ID（用于评论回复）
    content = Column(String(500), nullable=False)  # 评论内容
    created_at = Column(DateTime, default=datetime.now)  # 创建时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)  # 更新时间
    is_deleted = Column(Boolean, default=False)  # 软删除标记

    # 关系
    user = relationship("User", back_populates="comments")  # 关联用户
    post = relationship("Post", back_populates="comments")  # 关联帖子
    event = relationship("Event", back_populates="comments")  # 保持 "comments" 一致

    parent_comment = relationship("Comment", remote_side=[id], back_populates="replies")  # 关联父评论
    replies = relationship("Comment", back_populates="parent_comment", cascade="all, delete-orphan")  # 关联子评论
    def soft_delete(self):
        """ 软删除评论 """
        self.is_deleted = True
        self.content = "[评论已删除]"

class CommentLike(Base):
    __tablename__ = "comment_likes"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    comment_id = Column(Integer, ForeignKey("comments.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    user = relationship("User")
    comment = relationship("Comment")
