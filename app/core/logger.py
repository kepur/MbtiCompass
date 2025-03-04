import json
import logging
from datetime import datetime
from app.db.redis_client import redis_client

logger = logging.getLogger("fastapi")

def decode_message(message: str) -> str:
    """
    如果 message 是 JSON 字符串，则解析后重新生成，
    保证中文不被转义；否则直接返回原字符串。
    """
    try:
        # 如果 message 是个 JSON 字符串（以 { 开头），则尝试解析
        if message.strip().startswith("{"):
            obj = json.loads(message)
            return json.dumps(obj, ensure_ascii=False)
    except Exception:
        pass
    return message

def log_event(task_id: str, message: str, log_type: str = "info", is_task_log: bool = False):
    """
    记录日志 & 推送到 Redis

    :param task_id: 任务 ID（用于 WebSocket 订阅）
    :param message: 日志内容，可以是普通字符串或 JSON 字符串
    :param log_type: 日志级别 ("info", "warning", "error")
    :param is_task_log: 是否是任务日志
    """
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "task_id": task_id,
        "log_type": log_type,
        "message": message  # 此处 message 保持原样，作为最终推送给前端的内容
    }

    # 推送到 Redis 给前端 WebSocket 的日志，保持默认（Unicode 转义），前端解析后可显示中文
    ws_log = json.dumps(log_data)  # 默认 ensure_ascii=True
    channel = f"logs:{task_id}" if is_task_log else "logs"
    redis_client.publish(channel, ws_log)

    # 控制台输出时，我们希望看到正常的中文
    # 如果 message 是 JSON 字符串，我们先解析再重新生成
    log_data_console = {
        "timestamp": log_data["timestamp"],
        "task_id": log_data["task_id"],
        "log_type": log_data["log_type"],
        "message": decode_message(message)
    }
    console_log = json.dumps(log_data_console, ensure_ascii=False)
    logging.info(console_log)

    if is_task_log:
        # 推送任务日志到 Redis 队列时，也使用 ws_log
        redis_client.lpush(f"task_logs:{task_id}", ws_log)
        logging.info(console_log)

    # 如果不是任务日志，也通过 logger 输出原始 message
    if not is_task_log:
        if log_type == "info":
            logger.info(decode_message(message))
        elif log_type == "warning":
            logger.warning(decode_message(message))
        elif log_type == "error":
            logger.error(decode_message(message))
