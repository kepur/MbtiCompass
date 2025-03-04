import ffmpeg
import os

# 视频压缩
def compress_video(input_path, output_path, bitrate="800k"):
    ffmpeg.input(input_path).output(output_path, video_bitrate=bitrate, vcodec="libx264", preset="fast").run()

# 视频 AES 加密
def encrypt_file(input_path, output_path, key):
    cipher = Fernet(key)
    with open(input_path, "rb") as f:
        encrypted_data = cipher.encrypt(f.read())
    with open(output_path, "wb") as f:
        f.write(encrypted_data)
