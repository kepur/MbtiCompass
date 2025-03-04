import os
import redis
import logging
from app.core.config import settings
# 获取 Redis 配置
REDIS_HOST = settings.REDIS_HOST
REDIS_PORT = settings.REDIS_PORT
REDIS_DB = settings.REDIS_DB_BROKER
REDIS_PASSWORD = settings.REDIS_PASSWORD
# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("redis")

def get_redis_connection():
    """ 获取 Redis 连接 """
    logger.info(f"redis host: {REDIS_HOST} port: {REDIS_PORT} db: {REDIS_DB}")
    try:
        redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            password=REDIS_PASSWORD,
            decode_responses=True,
        )
        # 测试连接
        redis_client.ping()
        logger.info(f"✅ 连接 Redis 成功: {REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}")
        return redis_client
    except redis.ConnectionError as e:
        logger.error(f"❌ 无法连接 Redis: {REDIS_HOST}:{REDIS_PORT} - {e}")
        return None

# 连接 Redis
redis_client = get_redis_connection()
