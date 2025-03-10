from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.base import get_async_db
from app.models.user_model import User, UserRole
from app.models.location_model import UserLocation
from app.schemas.user_schema import UserResponse, UserUpdate
from app.core.security import hash_password,get_current_user, get_admin_user


user_router = APIRouter(prefix="/user", tags=["Users"])

@user_router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_async_db), current_user: User = Depends(get_current_user)):
    """ ✅ 获取用户（管理员可以查所有人，普通用户只能查自己） """
    async with db:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")

        # 普通用户只能获取自己的信息
        if current_user.role != UserRole.ADMIN and current_user.id != user_id:
            raise HTTPException(status_code=403, detail="无权限访问")

        return user

@user_router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_data: UserUpdate, db: AsyncSession = Depends(get_async_db), current_user: User = Depends(get_current_user)):
    """ ✅ 更新用户（用户只能改自己的信息，管理员可以改所有人） """
    async with db:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")

        if current_user.role != UserRole.ADMIN and current_user.id != user_id:
            raise HTTPException(status_code=403, detail="无权限修改此用户")

        if user_data.email:
            user.email = user_data.email
        if user_data.phone:
            user.phone = user_data.phone
        if user_data.password:
            user.hashed_password = hash_password(user_data.password)

        await db.commit()
        await db.refresh(user)

        return user

@user_router.delete("/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_async_db), current_user: User = Depends(get_admin_user)):
    """ ✅ 仅管理员可以删除用户 """
    async with db:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")

        await db.delete(user)
        await db.commit()
        return {"message": "用户已删除"}

@user_router.put("/{user_id}/deactivate")
async def deactivate_user(user_id: int, db: AsyncSession = Depends(get_async_db), current_user: User = Depends(get_current_user)):
    """ ✅ 用户注销（逻辑删除：is_active=False） """
    async with db:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")

        if current_user.role != UserRole.ADMIN and current_user.id != user_id:
            raise HTTPException(status_code=403, detail="无权限注销此用户")

        user.is_active = False
        await db.commit()
        return {"message": "账户已注销"}


@user_router.post("/update-location/")
def update_user_location(user_id: int, latitude: float, longitude: float, country: str, city: str, address: str, db: AsyncSession = Depends(get_async_db)):
    """
    更新用户的地理位置，每 1 小时调用一次
    """
    user_location = db.query(UserLocation).filter(UserLocation.user_id == user_id).first()

    if user_location:
        user_location.latitude = latitude
        user_location.longitude = longitude
        user_location.country = country
        user_location.city = city
        user_location.address = address
    else:
        new_location = UserLocation(
            user_id=user_id,
            latitude=latitude,
            longitude=longitude,
            country=country,
            city=city,
            address=address
        )
        db.add(new_location)

    db.commit()
    return {"status": "success"}
