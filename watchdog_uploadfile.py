import os
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from app.tasks.check_m3u8_handler import check_m3u8
from app.tasks.process_convert_2_ts import segment_video
from qcloud_cos import CosConfig, CosS3Client
from app.config import settings

# 配置日志输出
log_dir = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, time.strftime("%Y-%m-%d") + ".log")

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("watchdog")

# 腾讯云 OSS 配置（可改为读取 config.ini）
SECRET_ID = settings.ACCESS_KEY_ID
SECRET_KEY = settings.ACCESS_KEY_SECRET
REGION = settings.JAPAN_REGION
BUCKET = settings.JAPAN_BUCKET_NAME
OSS_PREFIX = "/v1/vol/"

cos_config = CosConfig(Region=REGION, SecretId=SECRET_ID, SecretKey=SECRET_KEY)
cos_client = CosS3Client(cos_config)

def is_file_fully_written(file_path, wait_time=3, max_retries=5, check_interval=1):
    """
    检查文件是否完全写入完成
    :param file_path: 文件路径
    :param wait_time: 初始等待时间（秒）
    :param max_retries: 最大重试次数
    :param check_interval: 检查间隔（秒）
    :return: bool 是否写入完成
    """
    try:
        # 1️⃣ 首先等待一段时间，让文件系统完成写入
        time.sleep(wait_time)
        
        # 2️⃣ 检查文件是否存在
        if not os.path.exists(file_path):
            logger.warning(f"❌ 文件不存在: {file_path}")
            return False
            
        # 3️⃣ 获取初始文件大小
        size1 = os.path.getsize(file_path)
        if size1 == 0:
            logger.warning(f"⚠️ 文件大小为0: {file_path}")
            return False
            
        # 4️⃣ 多次检查文件大小是否稳定
        for i in range(max_retries):
            time.sleep(check_interval)
            size2 = os.path.getsize(file_path)
            
            # 如果文件大小相同，说明写入完成
            if size1 == size2:
                # 额外检查文件是否可访问
                try:
                    with open(file_path, 'rb') as f:
                        f.seek(0, 2)  # 移动到文件末尾
                    logger.info(f"✅ 文件写入完成: {file_path}, 大小: {size1} 字节")
                    return True
                except Exception as e:
                    logger.warning(f"⚠️ 文件访问异常: {file_path}, 错误: {e}")
                    continue
                    
            # 如果文件大小增加，更新size1继续检查
            elif size2 > size1:
                size1 = size2
                logger.info(f"📈 文件仍在写入: {file_path}, 当前大小: {size2} 字节")
            # 如果文件大小减小，说明可能有问题
            else:
                logger.warning(f"⚠️ 文件大小异常减小: {file_path}, 从 {size1} 变为 {size2}")
                return False
                
        logger.warning(f"⚠️ 文件写入超时: {file_path}, 最终大小: {size1} 字节")
        return False
        
    except Exception as e:
        logger.error(f"❌ 检查文件写入状态时出错: {file_path}, 错误: {e}")
        return False

def upload_to_oss(file_path, base_path):
    try:
        # 相对于监听目录的路径（用于构造 OSS 路径）
        relative_path = os.path.relpath(file_path, base_path).replace("\\", "/")
        subdir = "7" if "720p" in base_path else "10"
        key = f"{OSS_PREFIX}{subdir}/{relative_path}"
        logger.info(f"📤 上传文件到 OSS: {key}")
        cos_client.upload_file(
            Bucket=BUCKET,
            LocalFilePath=file_path,
            Key=key
        )
        logger.info(f"✅ 上传完成: {key}")
    except Exception as e:
        logger.error(f"❌ 上传失败: {file_path} -> {e}")



class UploadEventHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory: return
        file_path = event.src_path
        logger.info(f"📥 检测到新上传文件: {file_path}")
        while not is_file_fully_written(file_path):
            logger.info(f"⏳ 等待上传文件写入完成: {file_path}")
            time.sleep(1)
        logger.info(f"✅ 上传文件写入完成，开始处理: {file_path}")
        segment_video.send(file_path)

class M3U8EventHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory or not event.src_path.endswith(".m3u8"): return
        file_path = event.src_path
        logger.info(f"🎬 新增 M3U8 文件: {file_path}")
        while not is_file_fully_written(file_path):
            logger.info(f"⏳ 等待 M3U8 写入完成: {file_path}")
            time.sleep(1)
        logger.info(f"✅ M3U8 写入完成，发送任务: {file_path}")
        check_m3u8.send(file_path)

class EncryptedFileEventHandler(FileSystemEventHandler):
    def __init__(self, base_dir):
        self.base_dir = base_dir  # 用于相对路径构造 OSS Key

    def on_created(self, event):
        if event.is_directory:
            # 是新目录，递归处理里面已有的文件
            for root, dirs, files in os.walk(event.src_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    self.process_file(file_path)
        else:
            self.process_file(event.src_path)

    def process_file(self, file_path):
        logger.info(f"🛡️ 新加密文件: {file_path}")
        while not is_file_fully_written(file_path):
            logger.info(f"⏳ 等待加密文件写入完成: {file_path}")
            time.sleep(1)
        logger.info(f"✅ 加密文件写入完成，准备上传 OSS: {file_path}")
        upload_to_oss(file_path, self.base_dir)


if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # 上传监听目录
    upload_dirs = [
        os.path.join(BASE_DIR, "MbtiCompass", "app", "static", "upload", sub)
        # for sub in ["chatimg", "chatvcr", "chatvol", "timeline"]
        for sub in [ "vods"]
    ]

    # M3U8 输出目录
    m3u8_dirs = [
        os.path.join(BASE_DIR, "MbtiCompass", "app", "static", "convert", "vods", sub)
        for sub in ["720p", "1080p"]
    ]

    # 加密后输出目录
    encrypted_dirs = [
        os.path.join(BASE_DIR, "MbtiCompass", "app", "static", "encryption", "vods", sub)
        for sub in ["720p", "1080p"]
    ]

    observer = Observer()
    logger.info("🚀 启动监听器...")

    for d in upload_dirs:
        os.makedirs(d, exist_ok=True)
        logger.info(f"👁️ 监听上传目录（递归）: {d}")
        observer.schedule(UploadEventHandler(), path=d, recursive=True)

    for d in m3u8_dirs:
        os.makedirs(d, exist_ok=True)
        logger.info(f"🎞️ 监听 M3U8 目录（递归）: {d}")
        observer.schedule(M3U8EventHandler(), path=d, recursive=True)

    for d in encrypted_dirs:
        os.makedirs(d, exist_ok=True)
        logger.info(f"🛡️ 监听加密输出目录（递归）: {d}")
        observer.schedule(EncryptedFileEventHandler(base_dir=d), path=d, recursive=True)

    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.warning("🛑 中止监听，退出中...")
        observer.stop()
    observer.join()

'''
# 示例：按时间切片，每 10 秒一片
generate_segments("input.mp4", "segment_%03d.ts", mode="time", value=10)
segment_video.send("input.mp4", mode="time", value=10)

# 示例：按大小切片，每片约 5MB
generate_segments("input.mp4", "segment_%03d.ts", mode="size", value=5 * 1024 * 1024)
segment_video.send("input.mp4", mode="size", value=5 * 1024 * 1024)
'''