from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.base import get_async_db
from app.models.user_model import Tag, User, User_Tags,UserRole
from app.schemas.user_schema import TagCreate, TagUpdate
from app.core.security import get_current_user,get_admin_user
from datetime import datetime, timedelta
from sqlalchemy import func
from app.core.logger import log_event

tags_router = APIRouter(prefix="/tags", tags=["Tags"])

@tags_router.get("/")
async def get_tags(db: AsyncSession = Depends(get_async_db)):
    """ ✅ 获取所有标签 """
    tags = await db.execute(select(Tag))
    return tags.scalars().all()

@tags_router.post("/create")
async def user_create_tag(
    tag_data: TagCreate,
    request: Request,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """ ✅ 用户创建标签并自动关联 """

    client_ip = request.client.host  # 获取 IP 地址

    # 1️⃣ **IP 限制：1 小时最多 20 次**
    ip_count = await db.execute(
        select(func.count()).where(Tag.created_at > datetime.now() - timedelta(hours=1))
    )
    if ip_count.scalar() >= 20:
        log_event("user_create_tag", message=f"❌ IP {client_ip} 请求过多", log_type="error")
        raise HTTPException(status_code=429, detail="IP 限制，请稍后再试")

    # 2️⃣ **用户限制：1 小时最多 10 次**
    user_count = await db.execute(
        select(func.count()).where(Tag.user_id == current_user.id, Tag.created_at > datetime.now() - timedelta(hours=1))
    )
    if user_count.scalar() >= 10:
        log_event("user_create_tag", message=f"❌ 用户 {current_user.id} 创建太频繁", log_type="error")
        raise HTTPException(status_code=429, detail="用户限制，请稍后再试")

    # 3️⃣ **频率限制：1 分钟最多 5 次**
    frequency_count = await db.execute(
        select(func.count()).where(Tag.user_id == current_user.id, Tag.created_at > datetime.now() - timedelta(minutes=1))
    )
    if frequency_count.scalar() >= 5:
        log_event("user_create_tag", message=f"❌ 用户 {current_user.id} 频率过高", log_type="error")
        raise HTTPException(status_code=429, detail="频率限制，请稍后再试")

    # 4️⃣ **检查是否已有该标签**
    existing_tag = await db.execute(select(Tag).where(Tag.name == tag_data.name))
    existing_tag = existing_tag.scalars().first()

    if existing_tag:
        log_event("user_create_tag", message=f"❌ 标签 '{tag_data.name}' 已存在", log_type="error")
        raise HTTPException(status_code=400, detail="标签已存在")

    # 5️⃣ **创建新标签**
    new_tag = Tag(name=tag_data.name, created_at=datetime.now())
    db.add(new_tag)
    await db.commit()
    await db.refresh(new_tag)

    # 6️⃣ **自动关联用户与标签**
    user_tag = User_Tags.insert().values(user_id=current_user.id, tag_id=new_tag.id)
    await db.execute(user_tag)
    await db.commit()

    log_event("user_create_tag", message=f"✅ 用户 {current_user.id} 创建标签 {new_tag.name} 并自动关联", log_type="info")

    return {"message": "标签创建成功", "tag": new_tag}

@tags_router.post("/{tag_id}/link")
async def user_link_tag(
    tag_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """ ✅ 用户关联已有标签 """
    tag = await db.execute(select(Tag).where(Tag.id == tag_id))
    tag = tag.scalars().first()

    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")

    # 检查用户是否已关联
    existing_link = await db.execute(
        select(User_Tags).where(User_Tags.c.user_id == current_user.id, User_Tags.c.tag_id == tag_id)
    )
    if existing_link.scalar():
        raise HTTPException(status_code=400, detail="用户已关联此标签")

    # 创建关联
    user_tag = User_Tags.insert().values(user_id=current_user.id, tag_id=tag_id)
    await db.execute(user_tag)
    await db.commit()

    log_event("user_link_tag", message=f"✅ 用户 {current_user.id} 关联了标签 {tag.name}", log_type="info")

    return {"message": "标签关联成功", "tag": tag}

@tags_router.put("/{tag_id}/update")
async def update_tag(
    tag_id: int,
    tag_data: TagUpdate,
    db: AsyncSession = Depends(get_async_db),
    admin_user: User = Depends(get_admin_user),  # ✅ 仅限管理员
    current_user: User = Depends(get_current_user)
):
    """ ✅ 更新标签（仅限创建者） """
    tag = await db.execute(select(Tag).where(Tag.id == tag_id))
    tag = tag.scalars().first()

    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")

    # 仅允许创建者 和管理员 修改
    if current_user.id != tag.user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="无权限修改该标签")

    tag.name = tag_data.name or tag.name
    tag.updated_at = datetime.now()

    db.add(tag)
    await db.commit()
    await db.refresh(tag)

    log_event("update_tag", message=f"✅ 用户 {admin_user.id} 更新了标签 {tag.name}", log_type="info")

    return {"message": "标签已更新", "tag": tag}

@tags_router.delete("/{tag_id}")
async def delete_tag(
    tag_id: int,
    db: AsyncSession = Depends(get_async_db),
    admin_user: User = Depends(get_admin_user)  # ✅ 仅限管理员
):
    """ ✅ 仅管理员可删除标签 """
    tag = await db.execute(select(Tag).where(Tag.id == tag_id))
    tag = tag.scalars().first()

    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")

    # 删除标签和关联关系
    await db.execute(User_Tags.delete().where(User_Tags.c.tag_id == tag_id))
    await db.commit()

    await db.delete(tag)
    await db.commit()

    log_event("delete_tag", message=f"✅ 管理员 {admin_user.id} 删除了标签 {tag.name}", log_type="info")

    return {"message": "标签已删除"}