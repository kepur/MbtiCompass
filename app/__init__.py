import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.dramatiq_setup import *  # 确保最先加载 broker 配置
from contextlib import asynccontextmanager
from app.config import settings
logger = logging.getLogger("uvicorn")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """ ✅ FastAPI 生命周期管理 """
    print("🚀 FastAPI 正在启动...")
    logger.info("✅ 仅连接数据库，**不修改表结构**")

    yield  # 允许 API 继续运行

    print("🔴 FastAPI 正在关闭...")
    logger.info("🔒 关闭数据库连接")

def create_app() -> FastAPI:
    """ ✅ 创建 FastAPI 应用 """
    app = FastAPI(
        title="My FastAPI Project",
        description="A scalable FastAPI project using SQLModel",
        version="1.0.0",
        lifespan=lifespan,
    )

    @app.get("/")
    async def read_root():
        return {"message": "Hello, FastAPI!"}

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    env = os.getenv("ENV", "development")
    print(f"Running in {env} mode")
    # ✅ 添加 WebSocket 实时监听路由

    return app

app = create_app()
