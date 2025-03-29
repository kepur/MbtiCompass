from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy import create_engine,text  # ✅ 用于同步数据库引擎
from app.config import settings

# ✅ **同步数据库 URL**
SYNC_DATABASE_URL = settings.SYNC_DATABASE_URL

# ✅ **异步数据库 URL**
ASYNC_DATABASE_URL = settings.ASYNC_DATABASE_URL

# ✅ **同步引擎 & Session**
sync_engine = create_engine(
    SYNC_DATABASE_URL,
    echo=True,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_recycle=settings.DB_POOL_RECYCLE,
    pool_pre_ping=settings.DB_POOL_PRE_PING
)
SyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

# ✅ **异步引擎 & Session**
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_recycle=settings.DB_POOL_RECYCLE,
    pool_pre_ping=settings.DB_POOL_PRE_PING
)
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

# ✅ **同步方法：删除所有表并重建数据库**
def reset_database_sync():
    """同步方式删除所有表并重建数据库"""
    with sync_engine.connect() as connection:
        # 获取数据库中的所有表（不仅仅是 Base.metadata 定义的）
        result = connection.execute(text("SHOW TABLES"))
        all_tables = [row[0] for row in result]

        if all_tables:
            # 禁用外键约束
            connection.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
            # 删除所有表
            for table in all_tables:
                connection.execute(text(f"DROP TABLE IF EXISTS {table}"))
            # 恢复外键约束
            connection.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
            connection.commit()
        else:
            print("数据库中没有表可删除")

    # 重新创建所有表
    Base.metadata.create_all(sync_engine)
    print("数据库所有表已删除并重建")

# ✅ **异步方法：删除所有表并重建数据库**
async def reset_database_async():
    """异步方式删除所有表并重建数据库"""
    async with async_engine.connect() as connection:
        # 获取数据库中的所有表
        result = await connection.execute(text("SHOW TABLES"))
        all_tables = [row[0] for row in result]

        if all_tables:
            # 禁用外键约束
            await connection.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
            # 删除所有表
            for table in all_tables:
                await connection.execute(text(f"DROP TABLE IF EXISTS {table}"))
            # 恢复外键约束
            await connection.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
            await connection.commit()
        else:
            print("数据库中没有表可删除")

    # 异步创建所有表
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("数据库所有表已删除并重建")

# ✅ **验证方法：检查表是否删除并重建**
def verify_database_sync():
    """同步验证数据库状态"""
    with sync_engine.connect() as connection:
        result = connection.execute(text("SHOW TABLES"))
        tables = [row[0] for row in result]
        print(f"当前数据库中的表：{tables}")
        return tables

async def verify_database_async():
    """异步验证数据库状态"""
    async with async_engine.connect() as connection:
        result = await connection.execute(text("SHOW TABLES"))
        tables = [row[0] for row in result]
        print(f"当前数据库中的表：{tables}")
        return tables

if __name__ == '__main__':
    sync_db = get_sync_db()
    # async_db = get_async_db()
    reset_database_sync()