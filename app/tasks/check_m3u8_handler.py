
import dramatiq
from app.tasks.process_m3u8_crypto import process_m3u8_file

@dramatiq.actor
def check_m3u8(file_path: str, output_root: str = None):
    try:
        print(f"[check_m3u8] 检测到 m3u8 文件: {file_path}")
        new_m3u8_path, media_code = process_m3u8_file(file_path, output_root)
        print(f"[check_m3u8] 新 m3u8 文件: {new_m3u8_path}")
        print(f"[check_m3u8] 生成 media_code: {media_code}")
    except Exception as e:
        print(f"[check_m3u8] 处理异常: {e}")


