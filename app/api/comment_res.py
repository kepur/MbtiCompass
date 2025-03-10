from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from app.models.base import get_async_db
from app.models.comment_model import Comment
from app.models.user_model import User, UserRole
from app.schemas.comment_schema import CommentCreate, CommentUpdate, CommentResponse
from app.core.security import get_current_user, get_admin_user

comment_router = APIRouter(prefix="/comments", tags=["Comments"])

@comment_router.post("/", response_model=CommentResponse)
async def create_comment(comment_data: CommentCreate, db: AsyncSession = Depends(get_async_db), current_user: User = Depends(get_current_user)):
    """ ✅ 创建评论 """
    new_comment = Comment(**comment_data.model_dump(), user_id=current_user.id)  # 绑定当前用户
    db.add(new_comment)
    await db.commit()
    await db.refresh(new_comment)
    return new_comment

@comment_router.get("/", response_model=List[CommentResponse])
async def get_comments(
    db: AsyncSession = Depends(get_async_db),
    skip: int = Query(0, alias="offset"),
    limit: int = Query(10, alias="limit"),
    post_id: int = None,
    event_id: int = None
):
    """ ✅ 获取评论列表（分页 + 过滤） """
    query = select(Comment).where(Comment.is_deleted == False).offset(skip).limit(limit)

    if post_id:
        query = query.where(Comment.post_id == post_id)
    if event_id:
        query = query.where(Comment.event_id == event_id)

    result = await db.execute(query)
    return result.scalars().all()

@comment_router.get("/{comment_id}", response_model=CommentResponse)
async def get_comment(comment_id: int, db: AsyncSession = Depends(get_async_db)):
    """ ✅ 获取单个评论 """
    result = await db.execute(select(Comment).where(Comment.id == comment_id, Comment.is_deleted == False))
    comment = result.scalars().first()
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")
    return comment

@comment_router.put("/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """ ✅ 更新评论（仅限评论作者或管理员） """
    result = await db.execute(select(Comment).where(Comment.id == comment_id, Comment.is_deleted == False))
    comment = result.scalars().first()
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")

    # ✅ 仅管理员或作者可修改评论
    if current_user.role != UserRole.ADMIN and comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权限修改此评论")

    comment_data_dict = comment_data.model_dump(exclude_unset=True)
    for key, value in comment_data_dict.items():
        setattr(comment, key, value)

    await db.commit()
    await db.refresh(comment)
    return comment

@comment_router.delete("/{comment_id}")
async def delete_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """ ✅ 软删除评论（仅限评论作者或管理员） """
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalars().first()
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")

    # ✅ 仅管理员或作者可删除评论
    if current_user.role != UserRole.ADMIN and comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权限删除此评论")

    comment.is_deleted = True
    comment.content = "[评论已删除]"
    await db.commit()
    return {"message": "评论已删除"}
