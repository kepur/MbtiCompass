from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# ✅ 评论创建请求
class CommentCreate(BaseModel):
    user_id: int
    content: str
    parent_id: Optional[int] = None  # 可选的父评论 ID
    post_id: Optional[int] = None  # 可选的帖子 ID
    event_id: Optional[int] = None  # 可选的活动 ID

# ✅ 评论更新请求
class CommentUpdate(BaseModel):
    content: Optional[str] = None

# ✅ 评论响应模型
class CommentResponse(BaseModel):
    id: int
    user_id: int
    content: str
    parent_id: Optional[int] = None
    post_id: Optional[int] = None
    event_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    is_deleted: bool

    class Config:
        from_attributes = True
