from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from app.models.base import get_async_db
from app.models.post_model import Post, PostImage, PostVideo, PostAudio
from app.models.user_model import User, UserRole
from app.schemas.post_schema import PostCreate, PostUpdate, PostResponse
from app.core.security import get_current_user, get_admin_user

post_router = APIRouter(prefix="/posts", tags=["Posts"])


@post_router.post("/", response_model=PostResponse)
async def create_post(post_data: PostCreate, db: AsyncSession = Depends(get_async_db),
                      current_user: User = Depends(get_current_user)):
    """ ✅ 创建帖子，限制一个视频 OR 一个音频，图片不限制 """

    # 🚀 限制一个帖子不能同时有视频和音频
    if post_data.video and post_data.audio:
        raise HTTPException(status_code=400, detail="❌ 不能同时上传视频和音频！")

    new_post = Post(
        user_id=current_user.id,
        content=post_data.content,
        location_id=post_data.location_id
    )
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)

    # ✅ 添加图片
    for img_url in post_data.images:
        db.add(PostImage(post_id=new_post.id, image_url=img_url))

    # ✅ 添加视频（如果有）
    if post_data.video:
        db.add(PostVideo(post_id=new_post.id, video_url=post_data.video))

    # ✅ 添加音频（如果有）
    if post_data.audio:
        db.add(PostAudio(post_id=new_post.id, audio_url=post_data.audio))

    await db.commit()
    return new_post


@post_router.get("/", response_model=List[PostResponse])
async def get_posts(
        db: AsyncSession = Depends(get_async_db),
        skip: int = Query(0, alias="offset"),
        limit: int = Query(10, alias="limit")
):
    """ ✅ 获取帖子列表，支持分页 """
    result = await db.execute(select(Post).offset(skip).limit(limit))
    return result.scalars().all()


@post_router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, db: AsyncSession = Depends(get_async_db)):
    """ ✅ 获取单个帖子 """
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code=404, detail="帖子不存在")
    return post


@post_router.put("/{post_id}", response_model=PostResponse)
async def update_post(post_id: int, post_data: PostUpdate, db: AsyncSession = Depends(get_async_db),
                      current_user: User = Depends(get_current_user)):
    """ ✅ 更新帖子（仅限作者或管理员） """
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code=404, detail="帖子不存在")

    # 🚀 仅限作者或管理员修改
    if current_user.role != UserRole.ADMIN and post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权限修改此帖子")

    # ✅ 允许修改的字段
    if post_data.content:
        post.content = post_data.content
    if post_data.images:
        await db.execute(select(PostImage).where(PostImage.post_id == post_id).delete())
        for img_url in post_data.images:
            db.add(PostImage(post_id=post.id, image_url=img_url))

    if post_data.video:
        await db.execute(select(PostVideo).where(PostVideo.post_id == post_id).delete())
        db.add(PostVideo(post_id=post.id, video_url=post_data.video))

    if post_data.audio:
        await db.execute(select(PostAudio).where(PostAudio.post_id == post_id).delete())
        db.add(PostAudio(post_id=post.id, audio_url=post_data.audio))

    await db.commit()
    await db.refresh(post)
    return post


@post_router.delete("/{post_id}")
async def delete_post(post_id: int, db: AsyncSession = Depends(get_async_db),
                      current_user: User = Depends(get_current_user)):
    """ ✅ 仅管理员或作者可删除帖子 """
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code=404, detail="帖子不存在")

    if current_user.role != UserRole.ADMIN and post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权限删除此帖子")

    await db.delete(post)
    await db.commit()
    return {"message": "帖子已删除"}
