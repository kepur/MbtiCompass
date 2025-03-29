import os
import datetime
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.base import get_async_db
from app.models.user_model import User
from app.core.security import get_current_user
from app.config import settings
from app.models.post_model import Post
from app.core.logger import log_event
from pydantic import BaseModel

upload_router = APIRouter(prefix="/upload", tags=["File Uploads"])

def get_upload_dir(subfolder: str):
    now = datetime.datetime.now()
    ym = now.strftime('%y%m')
    upload_path = os.path.join(settings.BASE_UPLOAD_DIR, subfolder, ym)
    os.makedirs(upload_path, exist_ok=True)
    return upload_path

def generate_filename(user_id: int, post_id: int, collection_code: str, suffix: str) -> str:
    now = datetime.datetime.now()
    timestamp = now.strftime('%y%m%d%H')
    return f"u{user_id}_{timestamp}_{post_id}_{collection_code}.{suffix}"

@upload_router.post("/start/video")
async def start_video_upload(
    total_size: int = Form(...),
    collection_code: str = Form("0000"),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    log_event("upload", f"🎬 初始化视频上传 user={current_user.id}, size={total_size}, code={collection_code}")
    upload_dir = get_upload_dir("vods")
    new_post = Post(user_id=current_user.id, post_type="video", created_at=datetime.datetime.now())
    db.add(new_post)
    await db.flush()

    filename = generate_filename(current_user.id, new_post.id, collection_code, "mp4")
    file_path = os.path.join(upload_dir, filename)
    with open(file_path, "wb") as f:
        f.truncate(total_size)

    await db.commit()
    return {"message": "视频上传初始化成功", "post_id": new_post.id, "filename": filename, "file_path": file_path}

@upload_router.post("/start/audio")
async def start_audio_upload(
    total_size: int = Form(...),
    collection_code: str = Form("0000"),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    log_event("upload", f"🎧 初始化音频上传 user={current_user.id}, size={total_size}, code={collection_code}")
    upload_dir = get_upload_dir("vocs")
    new_post = Post(user_id=current_user.id, post_type="audio", created_at=datetime.datetime.now())
    db.add(new_post)
    await db.flush()

    filename = generate_filename(current_user.id, new_post.id, collection_code, "m4a")
    file_path = os.path.join(upload_dir, filename)
    with open(file_path, "wb") as f:
        f.truncate(total_size)

    await db.commit()
    return {"message": "音频上传初始化成功", "post_id": new_post.id, "filename": filename, "file_path": file_path}

@upload_router.post("/start/image")
async def start_image_upload(
    total_size: int = Form(...),
    collection_code: str = Form("0000"),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    log_event("upload", f"🖼️ 初始化图片上传 user={current_user.id}, size={total_size}, code={collection_code}")
    upload_dir = get_upload_dir("imgs")
    new_post = Post(user_id=current_user.id, post_type="image", created_at=datetime.datetime.now())
    db.add(new_post)
    await db.flush()

    filename = generate_filename(current_user.id, new_post.id, collection_code, "jpg")
    file_path = os.path.join(upload_dir, filename)
    with open(file_path, "wb") as f:
        f.truncate(total_size)

    await db.commit()
    return {"message": "图片上传初始化成功", "post_id": new_post.id, "filename": filename, "file_path": file_path}

@upload_router.post("/chunk/video")
async def upload_video_chunk(
    filename: str = Form(...),
    chunk_index: int = Form(...),
    total_chunks: int = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    valid_types = ["video/mp4"]
    if file.content_type not in valid_types and not filename.lower().endswith(".mp4"):
        raise HTTPException(status_code=400, detail="视频格式仅支持 mp4")
    log_event("upload", f"📦 上传视频分片: {filename} chunk={chunk_index}/{total_chunks}")
    upload_dir = get_upload_dir("vods")
    file_path = os.path.join(upload_dir, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=400, detail="视频文件未初始化")

    offset = chunk_index * settings.CHUNK_SIZE
    with open(file_path, "r+b") as f:
        f.seek(offset)
        f.write(await file.read())

    return {"message": f"视频分片 {chunk_index}/{total_chunks} 上传成功"}

@upload_router.post("/chunk/audio")
async def upload_audio_chunk(
    filename: str = Form(...),
    chunk_index: int = Form(...),
    total_chunks: int = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    if not filename.lower().endswith(".m4a"):
        raise HTTPException(status_code=400, detail="音频格式仅支持 m4a")
    log_event("upload", f"📦 上传音频分片: {filename} chunk={chunk_index}/{total_chunks}")
    upload_dir = get_upload_dir("vocs")
    file_path = os.path.join(upload_dir, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=400, detail="音频文件未初始化")

    offset = chunk_index * settings.CHUNK_SIZE
    with open(file_path, "r+b") as f:
        f.seek(offset)
        f.write(await file.read())

    return {"message": f"音频分片 {chunk_index}/{total_chunks} 上传成功"}

@upload_router.post("/chunk/image")
async def upload_image_chunk(
    filename: str = Form(...),
    chunk_index: int = Form(...),
    total_chunks: int = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    if not filename.lower().endswith((".jpg", ".jpeg", ".png")):
        raise HTTPException(status_code=400, detail="图片格式仅支持 jpg/jpeg/png")
    log_event("upload", f"📦 上传图片分片: {filename} chunk={chunk_index}/{total_chunks}")
    upload_dir = get_upload_dir("imgs")
    file_path = os.path.join(upload_dir, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=400, detail="图片文件未初始化")

    offset = chunk_index * settings.CHUNK_SIZE
    with open(file_path, "r+b") as f:
        f.seek(offset)
        f.write(await file.read())

    return {"message": f"图片分片 {chunk_index}/{total_chunks} 上传成功"}

class CompleteUploadBody(BaseModel):
    filename: str

@upload_router.post("/complete/video")
async def complete_video_upload(
    body: CompleteUploadBody,
    current_user: User = Depends(get_current_user)
):
    upload_dir = get_upload_dir("vods")
    file_path = os.path.join(upload_dir, body.filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=400, detail="视频文件未找到")
    log_event("upload", f"✅ 视频上传完成: {body.filename}")
    return {"message": "视频上传完成", "file_path": file_path, "filename": body.filename}

@upload_router.post("/complete/audio")
async def complete_audio_upload(
    body: CompleteUploadBody,
    current_user: User = Depends(get_current_user)
):
    upload_dir = get_upload_dir("vocs")
    file_path = os.path.join(upload_dir, body.filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=400, detail="音频文件未找到")
    log_event("upload", f"✅ 音频上传完成: {body.filename}")
    return {"message": "音频上传完成", "file_path": file_path, "filename": body.filename}

@upload_router.post("/complete/image")
async def complete_image_upload(
    body: CompleteUploadBody,
    current_user: User = Depends(get_current_user)
):
    upload_dir = get_upload_dir("imgs")
    file_path = os.path.join(upload_dir, body.filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=400, detail="图片文件未找到")
    log_event("upload", f"✅ 图片上传完成: {body.filename}")
    return {"message": "图片上传完成", "file_path": file_path, "filename": body.filename}