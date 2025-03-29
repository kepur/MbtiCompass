from fastapi import APIRouter
from .auth.auth_res import auth_router  # ✅ 用户管理 API
from .auth.user_res import user_router
from .comment_res import comment_router
from .post_res import post_router
from .tags_res import tags_router
from .match_res import match_router
from .auth.decode_res import decode_router
from .upload_res import upload_router
api_router = APIRouter()
# 注册所有子路由
api_router.include_router(auth_router)
api_router.include_router(upload_router)
api_router.include_router(decode_router)
api_router.include_router(user_router)
api_router.include_router(match_router)
api_router.include_router(comment_router)
api_router.include_router(post_router)
api_router.include_router(tags_router)