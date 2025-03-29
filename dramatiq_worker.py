from app.dramatiq_setup import *  # 确保 worker 启动前加载配置
from app.tasks.check_m3u8_handler import  check_m3u8 # 导入 actor 模块以注册 actor
from app.tasks.process_convert_2_ts import  segment_video # 导入 actor 模块以注册 actor

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting Dramatiq Worker...")

#启动方式
#dramatiq --processes 1 --threads 3 dramatiq_worker
