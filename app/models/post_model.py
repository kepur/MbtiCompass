from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text,Boolean
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


class MediaCollection(Base):
    __tablename__ = "media_collections"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)  # 合集标题
    description = Column(Text, nullable=True)    # 合集简介
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # 可为空：系统创建或匿名合集
    is_public = Column(Integer, default=1)       # 是否公开：1公开，0私密
    created_at = Column(DateTime, default=datetime.now)
    # 关系
    user = relationship("User", back_populates="collections", lazy="joined", foreign_keys=[user_id])
    posts = relationship("MediaCollectionItem", back_populates="collection", cascade="all, delete-orphan")


class MediaCollectionItem(Base):
    __tablename__ = "media_collection_items"
    id = Column(Integer, primary_key=True, index=True)
    collection_id = Column(Integer, ForeignKey("media_collections.id"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    sort_order = Column(Integer, default=0)  # 在合集中的顺序（越小越先播放）
    # 关系
    collection = relationship("MediaCollection", back_populates="posts")
    post = relationship("Post")


class PostImage(Base):
    __tablename__ = "post_images"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=True)  # 关联帖子 ID
    decode = Column(String(255), nullable=True)
    media_code = Column(String(255), nullable=False)  # 图片 URL，最大 255 字符
    uploaded_at = Column(DateTime, default=datetime.now)  # 上传时间
    post = relationship("Post", back_populates="images")  # 关联帖子表


class PostVideo(Base):
    __tablename__ = "post_videos"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=True, unique=True)  # 唯一约束，确保一对一
    definition = Column(Boolean, nullable=True,default=False)
    media_code = Column(String(255), nullable=False)  # 视频 URL，最大 255 字符
    uploaded_at = Column(DateTime, default=datetime.now)  # 上传时间
    post = relationship("Post", back_populates="video")  # 关联帖子表


class PostAudio(Base):
    __tablename__ = "post_audios"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=True, unique=True)  # 唯一约束，确保一对一
    decode = Column(String(255), nullable=True)
    media_code = Column(String(255), nullable=False)  # 音频 URL，最大 255 字符
    uploaded_at = Column(DateTime, default=datetime.now)  # 上传时间
    post = relationship("Post", back_populates="audio")  # 修正为 "audio"