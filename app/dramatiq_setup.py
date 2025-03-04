import dramatiq
from dramatiq.brokers.redis import RedisBroker
import redis
import logging
from app.config import settings

# 配置 Redis Broker
redis_broker = RedisBroker(url=settings.REDIS_URL)
dramatiq.set_broker(redis_broker)

# **清除默认中间件**
dramatiq.middleware.default_middleware.clear()

# **连接 Redis**
redis_client = redis.StrictRedis.from_url(settings.REDIS_URL, decode_responses=True)

# **启动时清除 Redis 中的旧任务**
def clear_old_tasks(custom_keys=None):
    if custom_keys is None:
        # 如果没有传入自定义 key 列表，默认清除所有 Dramatiq 相关任务
        keys = redis_client.keys("dramatiq:*")
    else:
        # 使用传入的自定义 key 列表
        keys = custom_keys

    if keys:
        redis_client.delete(*keys)  # 删除它们
        print(f"✅ 清除 {len(keys)} 个遗留任务")
    else:
        print("✅ 没有需要清理的任务")

# 示例：自定义 key 列表
custom_keys = ["update_baseinfo*", "update_market_data*", "init_logo_data*","task_lock*"]
clear_old_tasks(custom_keys)  # 清除自定义的 key

# **调用清理函数**
clear_old_tasks()

class UniqueQueueMiddleware(dramatiq.Middleware):
    def before_enqueue(self, broker, message, delay=None):
        """任务入队前检查 Redis 是否已有相同任务"""
        task_id = message.args[1] if len(message.args) > 1 else None
        if not task_id:
            return True  # 没有 task_id，正常入队

        task_key = f"coin_task:{task_id}"

        if redis_client.exists(task_key):
            logging.info(f"任务 {task_id} 已存在于队列中，跳过入队")
            return False  # **跳过入队**

        redis_client.setex(task_key, 600, "processing")  # **10 分钟过期**
        return True

    def after_enqueue(self, broker, message, delay=None):
        """任务成功入队时的日志记录"""
        task_id = message.args[1] if len(message.args) > 1 else None
        if task_id:
            logging.info(f"任务 {task_id} 已加入队列")

    def after_process(self, broker, message, result, exception):
        """任务处理完成后，从 Redis 中删除任务标识"""
        task_id = message.args[1] if len(message.args) > 1 else None
        if task_id:
            redis_client.delete(f"coin_task:{task_id}")
            logging.info(f"任务 {task_id} 处理完成，从 Redis 中移除")

# **注册自定义去重中间件**
redis_broker.add_middleware(UniqueQueueMiddleware())
