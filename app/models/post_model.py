from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=True)  # 帖子文本内容
    post_type = Column(String, nullable=False)  # "text", "image", "video"

    location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)  # 可选的位置信息
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    user = relationship("User", back_populates="posts")
    location = relationship("Location", back_populates="posts")
    images = relationship("PostImage", back_populates="post", cascade="all, delete-orphan")
    videos = relationship("PostVideo", back_populates="post", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="post")  # 帖子的所有评论

class PostImage(Base):
    __tablename__ = "post_images"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    image_url = Column(String, nullable=False)  # 图片URL
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    post = relationship("Post", back_populates="images")


class PostVideo(Base):
    __tablename__ = "post_videos"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    video_url = Column(String, nullable=False)  # 视频URL
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    post = relationship("Post", back_populates="videos")
