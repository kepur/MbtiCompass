from pydantic import BaseModel, Field
from typing import Optional
from app.models.enums_model import GenderEnum, EducationEnum

class MatchPreferenceCreate(BaseModel):
    """ ✅ 创建匹配偏好 """
    min_age: int = Field(default=18, ge=18, le=100, description="允许的最小年龄，默认为 18 岁")
    max_age: int = Field(default=40, ge=18, le=100, description="允许的最大年龄，默认为 40 岁")
    gender: Optional[GenderEnum] = Field(default=None, description="期望匹配的性别")
    education_preference: Optional[EducationEnum] = Field(default=None, description="期望的学历要求")
    preferred_hobbies: Optional[str] = Field(default=None, description="用户偏好的兴趣爱好，以文本形式存储")
    max_distance: Optional[float] = Field(default=None, description="允许的最大匹配距离（单位：公里）")

class MatchPreferenceUpdate(BaseModel):
    """ ✅ 更新匹配偏好（所有字段可选） """
    min_age: Optional[int] = Field(default=None, ge=18, le=100, description="允许的最小年龄")
    max_age: Optional[int] = Field(default=None, ge=18, le=100, description="允许的最大年龄")
    gender: Optional[GenderEnum] = Field(default=None, description="期望匹配的性别")
    education_preference: Optional[EducationEnum] = Field(default=None, description="期望的学历要求")
    preferred_hobbies: Optional[str] = Field(default=None, description="用户偏好的兴趣爱好")
    max_distance: Optional[float] = Field(default=None, description="允许的最大匹配距离（单位：公里）")

class MatchPreferenceResponse(MatchPreferenceCreate):
    """ ✅ 返回匹配偏好数据（继承 `MatchPreferenceCreate` 并添加 `user_id`） """
    user_id: int = Field(..., description="匹配偏好的用户 ID")
