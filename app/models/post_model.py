from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 关联用户 ID
    content = Column(Text, nullable=True)  # 帖子文本内容（可选）
    post_type = Column(String(20), nullable=False)  # 帖子类型，例如 "text", "image", "video"

    location_id = Column(Integer, ForeignKey("user_locations.id"), nullable=True)  # 关联的位置信息（可选）
    created_at = Column(DateTime, default=datetime.utcnow)  # 创建时间

    # 关系
    user = relationship("User", back_populates="posts")  # 关联用户表
    location = relationship("Location", back_populates="posts")  # 关联位置信息表
    images = relationship("PostImage", back_populates="post", cascade="all, delete-orphan")  # 关联图片列表
    videos = relationship("PostVideo", back_populates="post", cascade="all, delete-orphan")  # 关联视频列表
    comments = relationship("Comment", back_populates="post")  # 关联评论

class PostImage(Base):
    __tablename__ = "post_images"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)  # 关联帖子 ID
    image_url = Column(String(255), nullable=False)  # 图片 URL，最大 255 字符
    uploaded_at = Column(DateTime, default=datetime.utcnow)  # 上传时间

    post = relationship("Post", back_populates="images")  # 关联帖子表

class PostVideo(Base):
    __tablename__ = "post_videos"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)  # 关联帖子 ID
    video_url = Column(String(255), nullable=False)  # 视频 URL，最大 255 字符
    uploaded_at = Column(DateTime, default=datetime.utcnow)  # 上传时间

    post = relationship("Post", back_populates="videos")  # 关联帖子表
