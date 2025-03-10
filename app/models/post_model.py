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
    created_at = Column(DateTime, default=datetime.now)  # 创建时间

    # 关系
    user = relationship("User", back_populates="posts")
    location = relationship("UserLocation", back_populates="posts")  # 一个位置多个帖子
    # 一对多：多个图片
    images = relationship("PostImage", back_populates="post", cascade="all, delete-orphan")
    # 一对一：一个视频
    video = relationship("PostVideo", back_populates="post", uselist=False, cascade="all, delete-orphan")
    # 一对一：一个音频
    audio = relationship("PostAudio", back_populates="post", uselist=False, cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="post")  # 关联评论


class PostImage(Base):
    __tablename__ = "post_images"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)  # 关联帖子 ID
    local_file_path = Column(String(255), nullable=True)
    image_url = Column(String(255), nullable=False)  # 图片 URL，最大 255 字符
    uploaded_at = Column(DateTime, default=datetime.now)  # 上传时间
    post = relationship("Post", back_populates="images")  # 关联帖子表


class PostVideo(Base):
    __tablename__ = "post_videos"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False, unique=True)  # 唯一约束，确保一对一
    local_file_path = Column(String(255), nullable=True)
    video_url = Column(String(255), nullable=False)  # 视频 URL，最大 255 字符
    uploaded_at = Column(DateTime, default=datetime.now)  # 上传时间
    post = relationship("Post", back_populates="video")  # 关联帖子表


class PostAudio(Base):
    __tablename__ = "post_audios"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False, unique=True)  # 唯一约束，确保一对一
    local_file_path = Column(String(255), nullable=True)
    audio_url = Column(String(255), nullable=False)  # 音频 URL，最大 255 字符
    uploaded_at = Column(DateTime, default=datetime.now)  # 上传时间
    post = relationship("Post", back_populates="audio")  # 修正为 "audio"