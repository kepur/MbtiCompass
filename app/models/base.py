from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy import create_engine  # ✅ 用于同步数据库引擎
from app.config import settings

# ✅ **同步数据库 URL**
SYNC_DATABASE_URL = settings.SYNC_DATABASE_URL

# ✅ **异步数据库 URL**
ASYNC_DATABASE_URL = settings.ASYNC_DATABASE_URL


# ✅ **同步引擎 & Session**
sync_engine = create_engine(SYNC_DATABASE_URL, echo=True)
SyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

# ✅ **异步引擎 & Session**
async_engine = create_async_engine(ASYNC_DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(async_engine, expire_on_commit=False)

# ✅ **定义 Base 类（同步 & 异步通用）**
class Base(DeclarativeBase):
    pass

# ✅ **获取同步会话**
def get_sync_db():
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ **获取异步会话**
async def get_async_db():
    async with AsyncSessionLocal() as db:
        yield db