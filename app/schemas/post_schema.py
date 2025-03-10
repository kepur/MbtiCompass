from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# ✅ 图片模型
class PostImageResponse(BaseModel):
    id: int
    image_url: str
    uploaded_at: datetime

    class Config:
        from_attributes = True

# ✅ 视频模型
class PostVideoResponse(BaseModel):
    id: int
    video_url: str
    uploaded_at: datetime

    class Config:
        from_attributes = True

# ✅ 音频模型
class PostAudioResponse(BaseModel):
    id: int
    audio_url: str
    uploaded_at: datetime

    class Config:
        from_attributes = True

# ✅ 创建帖子请求
class PostCreate(BaseModel):
    content: Optional[str] = None
    location_id: Optional[int] = None  # 关联位置信息
    images: List[str] = Field(default_factory=list)  # ✅ 允许多个图片
    video: Optional[str] = None  # ✅ 仅允许 1 个视频
    audio: Optional[str] = None  # ✅ 仅允许 1 个音频

    @staticmethod
    def validate_media(video: Optional[str], audio: Optional[str]):
        if video and audio:
            raise ValueError("❌ 不能同时上传视频和音频！")

# ✅ 更新帖子请求
class PostUpdate(BaseModel):
    content: Optional[str] = None
    images: List[str] = Field(default_factory=list)
    video: Optional[str] = None
    audio: Optional[str] = None

# ✅ 帖子响应模型
class PostResponse(BaseModel):
    id: int
    user_id: int
    content: Optional[str] = None
    location_id: Optional[int] = None
    created_at: datetime
    images: List[PostImageResponse] = []
    video: Optional[PostVideoResponse] = None
    audio: Optional[PostAudioResponse] = None

    class Config:
        from_attributes = True
