from PIL import Image
from io import BytesIO
from cryptography.fernet import Fernet
import base64

# 生成 AES 加密密钥（仅需执行一次）
def generate_key():
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)
    return key

# 读取 AES 密钥
def load_key():
    return open("secret.key", "rb").read()

# 图片压缩
def compress_image(image_path, quality=50):
    img = Image.open(image_path)
    img = img.convert("RGB")  # 确保是 RGB 格式
    output = BytesIO()
    img.save(output, format="JPEG", quality=quality)
    return output.getvalue()

# AES 加密
def encrypt_data(data, key):
    cipher = Fernet(key)
    return cipher.encrypt(data)

# 处理图片
def process_image(image_path):
    key = load_key()  # 读取 AES 密钥
    compressed_image = compress_image(image_path)
    encrypted_image = encrypt_data(compressed_image, key)
    return encrypted_image
