from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.base import get_async_db
from app.models.match_model import MatchPreference
from app.models.user_model import User
from app.schemas.match_schema import MatchPreferenceCreate, MatchPreferenceUpdate, MatchPreferenceResponse
from app.core.security import get_current_user
from datetime import datetime
from app.core.logger import log_event

match_router = APIRouter(prefix="/match", tags=["Match"])

@match_router.get("", response_model=MatchPreferenceResponse)
async def get_user_match_preference(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """ ✅ 获取当前用户的匹配偏好 """
    preference = await db.execute(select(MatchPreference).where(MatchPreference.user_id == current_user.id))
    preference = preference.scalars().first()

    if not preference:
        raise HTTPException(status_code=404, detail="未设置匹配偏好")

    return preference

@match_router.post("", response_model=MatchPreferenceResponse)
async def create_match_preference(
    preference_data: MatchPreferenceCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """ ✅ 创建或更新用户的匹配偏好 """
    existing_preference = await db.execute(select(MatchPreference).where(MatchPreference.user_id == current_user.id))
    existing_preference = existing_preference.scalars().first()

    if existing_preference:
        raise HTTPException(status_code=400, detail="匹配偏好已存在，可使用更新接口")

    new_preference = MatchPreference(
        user_id=current_user.id,
        min_age=preference_data.min_age,
        max_age=preference_data.max_age,
        gender=preference_data.gender,
        education_preference=preference_data.education_preference,
        preferred_hobbies=preference_data.preferred_hobbies,
        max_distance=preference_data.max_distance
    )

    db.add(new_preference)
    await db.commit()
    await db.refresh(new_preference)

    log_event("create_match_preference", message=f"✅ 用户 {current_user.id} 设置了匹配偏好", log_type="info")

    return new_preference

@match_router.put("", response_model=MatchPreferenceResponse)
async def update_match_preference(
    preference_data: MatchPreferenceUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """ ✅ 更新用户的匹配偏好 """
    preference = await db.execute(select(MatchPreference).where(MatchPreference.user_id == current_user.id))
    preference = preference.scalars().first()

    if not preference:
        raise HTTPException(status_code=404, detail="未找到匹配偏好")

    preference.min_age = preference_data.min_age or preference.min_age
    preference.max_age = preference_data.max_age or preference.max_age
    preference.gender = preference_data.gender or preference.gender
    preference.education_preference = preference_data.education_preference or preference.education_preference
    preference.preferred_hobbies = preference_data.preferred_hobbies or preference.preferred_hobbies
    preference.max_distance = preference_data.max_distance or preference.max_distance

    db.add(preference)
    await db.commit()
    await db.refresh(preference)

    log_event("update_match_preference", message=f"✅ 用户 {current_user.id} 更新了匹配偏好", log_type="info")

    return preference

@match_router.delete("")
async def delete_match_preference(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """ ✅ 删除用户的匹配偏好 """
    preference = await db.execute(select(MatchPreference).where(MatchPreference.user_id == current_user.id))
    preference = preference.scalars().first()

    if not preference:
        raise HTTPException(status_code=404, detail="未找到匹配偏好")

    await db.delete(preference)
    await db.commit()

    log_event("delete_match_preference", message=f"✅ 用户 {current_user.id} 删除了匹配偏好", log_type="info")

    return {"message": "匹配偏好已删除"}
