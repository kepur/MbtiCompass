# app/tasks/m3u8_crypto.py
import os
import re
import json
import base64
import hashlib
import hmac
from Crypto.Cipher import AES
from typing import Tuple
from app.config import settings
from app.models.user_model import User
from app.models.base import get_async_db
from app.core.logger import log_event
import datetime
from sqlalchemy.future import select
from app.models import PostVideo, MediaCollectionItem,Post
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio

# 获取项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def inster_mediainfo(user_id, post_id, dt, collection_code, media_code, definition=False):
    async def write_db():
        async with get_async_db() as db:
            # ✅ 检查 Post 是否存在（必须存在才能有 user_id）
            result = await db.execute(select(Post).where(Post.id == post_id))
            post = result.scalars().first()

            if not post:
                post = Post(
                    id=post_id,
                    user_id=user_id,
                    post_type="video",  # 你也可以动态传入
                    created_at=dt
                )
                db.add(post)

            # ✅ 插入 PostVideo（确保视频一对一）
            result = await db.execute(select(PostVideo).where(PostVideo.post_id == post_id))
            post_video = result.scalars().first()
            if not post_video:
                post_video = PostVideo(
                    post_id=post_id,
                    media_code=media_code,
                    definition=definition,
                    uploaded_at=dt
                )
                db.add(post_video)

            # ✅ 插入 MediaCollectionItem（非系统合集）
            if collection_code != "0000":
                collection_id = int(collection_code)
                result = await db.execute(select(MediaCollectionItem).where(
                    MediaCollectionItem.collection_id == collection_id,
                    MediaCollectionItem.post_id == post_id
                ))
                existing = result.scalars().first()
                if not existing:
                    collection_item = MediaCollectionItem(
                        collection_id=collection_id,
                        post_id=post_id,
                        sort_order=0
                    )
                    db.add(collection_item)

            await db.commit()

    # ⚠️ 注意：这个方法是 async 内嵌的，但没有调用
    # 所以在外部使用的时候要调用它：
    # await inster_mediainfo(...).write_db()
    return write_db


def parse_filename(filename: str):
    pattern = r"u(\d+)_(\d{8})_(\d+)_(\d{4})"
    match = re.match(pattern, filename)
    if not match:
        return None
    user_id, dt_str, post_id, collection_code = match.groups()
    dt = datetime.datetime.strptime(dt_str, "%y%m%d%H")
    return int(user_id), dt, int(post_id), collection_code

def get_current_ym_prefix():
    """
    返回当前年月字符串，格式如 '2408/'，表示2024年8月
    """
    now = datetime.datetime.now()
    return now.strftime('%y%m/')  # %y: 两位数年份, %m: 月份补零


def to_bytes(key):
    return key.encode() if isinstance(key, str) else key


def generate_chunk_code(filename: str) -> str:
    hash_digest = hashlib.sha1(filename.encode()).digest()
    hmac_digest = hmac.new(to_bytes(settings.MEDIA_SECRET_KEY), hash_digest, hashlib.sha256).digest()[:12]
    return base64.urlsafe_b64encode(hmac_digest).decode().rstrip("=")


def generate_chunk_name(chunk_code: str, index: int) -> str:
    hash_digest = hmac.new(to_bytes(settings.MEDIA_SECRET_KEY), f"{chunk_code}{index}".encode(), hashlib.sha1).digest()[:12]
    return base64.urlsafe_b64encode(hash_digest).decode().rstrip("=")[:16] + ".mct"


def pad(data: bytes) -> bytes:
    pad_len = 16 - len(data) % 16
    return data + bytes([pad_len] * pad_len)


def encrypt_aes128(input_path: str, output_path: str, key: bytes):
    cipher = AES.new(key, AES.MODE_CBC, iv=b'1234567890123456')
    with open(input_path, 'rb') as f:
        plaintext = f.read()
    padded = pad(plaintext)
    ciphertext = cipher.encrypt(padded)
    with open(output_path, 'wb') as f:
        f.write(ciphertext)


def shorten_floats(float_list, precision=1):
    return [round(f, precision) for f in float_list]


def process_m3u8_file(m3u8_path: str, output_root: str = None) -> Tuple[str, str]:
    with open(m3u8_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    ts_files = [line.strip() for line in lines if line.strip().endswith(".ts")]
    m3u8_dir = os.path.dirname(m3u8_path)
    base_filename = os.path.basename(m3u8_path)
    chunk_code = generate_chunk_code(base_filename)

    # ✅ 先生成 token（基于 chunk_code）
    token = base64.urlsafe_b64encode(
        hmac.new(to_bytes(settings.MEDIA_SECRET_KEY), chunk_code.encode(), hashlib.sha256).digest()[:8]
    ).decode().rstrip("=")

    # ✅ 然后用 token 派生 encryption_key（与解密端保持一致）
    encryption_key = hmac.new(to_bytes(settings.MEDIA_SECRET_KEY), token.encode(), hashlib.sha256).digest()[:16]

    # ✅ 构建解密用 key URI
    # key_uri = f"http://127.0.0.1:1992/mbticompass/decode/{token}"

    # 构建 key URI
    durations = []
    chunk_map = {}
    for i, ts_file in enumerate(ts_files):
        chunk_name = generate_chunk_name(chunk_code, i)
        chunk_map[ts_file] = chunk_name

    # 目标输出目录（按 720p/1080p 自动分类）
    rel = os.path.normpath(m3u8_path).split(os.sep)
    resolution = "720p" if "720p" in rel else "1080p"

    definition = False
    if "1080p" in rel:
        definition=True

    current_ym_prefix = get_current_ym_prefix()
    if output_root:
        output_dir = os.path.join(output_root, resolution,current_ym_prefix)
    else:
        output_dir = os.path.join(BASE_DIR, "static", "encryption", "vods", resolution,current_ym_prefix)

    os.makedirs(output_dir, exist_ok=True)

    # 加密 TS 并输出
    for ts_file, chunk_name in chunk_map.items():
        original_path = os.path.join(m3u8_dir, ts_file)
        if os.path.exists(original_path):
            encrypted_path = os.path.join(output_dir, chunk_name)
            encrypt_aes128(original_path, encrypted_path, encryption_key)

    # 构建新 m3u8 文件
    # new_lines = []
    # for line in lines:
    #     if line.startswith("#EXTINF"):
    #         duration = float(line.split(":")[1].split(",")[0])
    #         durations.append(duration)
    #         new_lines.append(f"#EXTINF:{round(duration, 1)},\n")
    #     elif line.strip().endswith(".ts"):
    #         chunk_name = chunk_map.get(line.strip())
    #         new_lines.append(f"{chunk_name}\n")
    #     else:
    #         new_lines.append(line)
    #
    # # 插入动态 URI 的 AES KEY
    # for i, line in enumerate(new_lines):
    #     if line.startswith("#EXT-X-PLAYLIST-TYPE"):
    #         new_lines.insert(i + 1, f'#EXT-X-KEY:METHOD=AES-128,URI="{token}"\n')
    #         break
    #
    # new_m3u8_path = os.path.join(output_dir, base_filename.replace(".m3u8", "_enc.m3u8"))
    # with open(new_m3u8_path, "w", encoding="utf-8") as f:
    #     f.writelines(new_lines)


    media_info = {
        "v": 3,
        "t": 8,
        "s": shorten_floats(durations),
        "c": len(ts_files),
        "m": chunk_code,
        "e": token,
        "d":current_ym_prefix
    }

    media_json = json.dumps(media_info, separators=(",", ":"))
    parsed = parse_filename(base_filename)
    media_code = base64.urlsafe_b64encode(media_json.encode()).decode().rstrip("=")
    if parsed:
        user_id, dt, post_id, collection_code = parsed
        inster_mediainfo(user_id, post_id, dt, collection_code, media_code,definition)

    # return new_m3u8_path, media_code
    return media_code