import os
import base64
import io
from PIL import Image
from pydub import AudioSegment
import ffmpeg
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import oss2

# 配置 OSS
ACCESS_KEY_ID = "your-access-key"
ACCESS_KEY_SECRET = "your-access-secret"
BUCKET_NAME = "your-bucket-name"
ENDPOINT = "oss-cn-shanghai.aliyuncs.com"

auth = oss2.Auth(ACCESS_KEY_ID, ACCESS_KEY_SECRET)
bucket = oss2.Bucket(auth, ENDPOINT, BUCKET_NAME)

# AES 加密密钥 (32 字节) 和 IV (16 字节)
AES_KEY = os.urandom(32)
AES_IV = os.urandom(16)

def encrypt_data(data: bytes) -> bytes:
    """AES-256-CBC 加密"""
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    encrypted = cipher.encrypt(pad(data, AES.block_size))
    return base64.b64encode(AES_IV + encrypted)  # 前16字节存 IV

def compress_image(input_path: str, quality=60) -> bytes:
    """压缩图片"""
    img = Image.open(input_path)
    img = img.convert("RGB")  # 确保是 RGB
    output = io.BytesIO()
    img.save(output, format="JPEG", quality=quality)
    return output.getvalue()

def compress_audio(input_path: str, output_format="mp3", bitrate="64k") -> bytes:
    """压缩音频"""
    audio = AudioSegment.from_file(input_path)
    output = io.BytesIO()
    audio.export(output, format=output_format, bitrate=bitrate)
    return output.getvalue()

def compress_video(input_path: str) -> bytes:
    """压缩视频"""
    output_path = "compressed.mp4"
    (
        ffmpeg.input(input_path)
        .output(output_path, vcodec="libx264", crf=28)  # CRF 值越高压缩率越高
        .run(overwrite_output=True)
    )
    with open(output_path, "rb") as f:
        return f.read()

def upload_file(file_path: str):
    """压缩 & 加密 & 上传"""
    ext_map = {".jpg": ".mci", ".png": ".mci", ".mp3": ".mca", ".wav": ".mca", ".mp4": ".mcv"}
    file_ext = os.path.splitext(file_path)[-1].lower()

    if file_ext not in ext_map:
        raise ValueError("不支持的文件格式")

    # 选择合适的压缩方法
    if file_ext in [".jpg", ".png"]:
        compressed_data = compress_image(file_path)
    elif file_ext in [".mp3", ".wav"]:
        compressed_data = compress_audio(file_path)
    elif file_ext in [".mp4"]:
        compressed_data = compress_video(file_path)
    else:
        raise ValueError("未知文件类型")

    # 加密
    encrypted_data = encrypt_data(compressed_data)

    # 生成新文件名
    new_file_name = os.path.basename(file_path).replace(file_ext, ext_map[file_ext])

    # 上传到 OSS
    bucket.put_object(new_file_name, encrypted_data)
    print(f"文件 {file_path} 已加密上传为 {new_file_name}")

# 示例上传
upload_file("test.jpg")  # 上传后变成 test.mci
upload_file("audio.mp3")  # 上传后变成 audio.mca
upload_file("video.mp4")  # 上传后变成 video.mcv
