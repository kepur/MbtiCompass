from fastapi import APIRouter
from .auth_res import auth_router  # ✅ 用户管理 API
from .user_res import user_router
from .comment_res import comment_router
from .article_res import post_router
api_router = APIRouter()
# 注册所有子路由
api_router.include_router(auth_router)
api_router.include_router(user_router)
api_router.include_router(comment_router)
api_router.include_router(post_router)
