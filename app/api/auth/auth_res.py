import random
import string
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.redis_client import redis_client  # 直接使用 Redis 连接
from app.models.base import get_async_db
from app.models.user_model import User
from app.schemas.user_schema import RegisterRequest, SendVerificationCodeRequest, TokenResponse,LoginRequest
from app.core.security import create_access_token, hash_password, verify_password
from app.config import settings  # 确保 settings 里有邮件配置
from app.core.logger import log_event
from fastapi.templating import Jinja2Templates
from app.services.mail_auth import send_email
from app.services.sms_auth import send_sms

templates = Jinja2Templates(directory="app/static/template")
auth_router = APIRouter(prefix="/auth", tags=["Auths"])


def generate_verification_code():
    """ 生成 6 位随机验证码 """
    return "".join(random.choices(string.digits, k=settings.CODE_LENGTH))


@auth_router.post("/send-verification-code/")
async def send_verification_code(
    user_data: SendVerificationCodeRequest, request: Request, background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_db)  # ✅ 依赖数据库
):
    """ ✅ 发送验证码（支持邮箱或手机号） """
    email = user_data.email
    phone_number = user_data.phone_number
    user_ip = request.client.host
    # 1️⃣ **检查邮箱或手机号是否已注册**
    async with db:
        query = select(User).where(
            (User.email == email) | (User.phone_number == phone_number)
        )
        result = await db.execute(query)
        existing_user = result.scalars().first()

    if existing_user:
        log_event("send_verification_code", message="❌ 该邮箱或手机号已注册", log_type="error")
        raise HTTPException(status_code=400, detail="该邮箱或手机号已注册")

    # ✅ 确保用户提供了邮箱或手机号
    if not email and not phone_number:
        log_event("send_verification_code", message="❌ 必须提供邮箱或手机号", log_type="error")
        raise HTTPException(status_code=400, detail="必须提供邮箱或手机号")

    # 1️⃣ **IP 限制：1 小时最多 5 次**
    ip_count_key = f"request_ip_count:{user_ip}"
    ip_request_count = redis_client.get(ip_count_key)

    if ip_request_count and int(ip_request_count) >= settings.MAX_IP_REQUESTS_PER_HOUR:
        log_event("send_verification_code", message=f"❌ {user_ip} 请求过于频繁", log_type="error")
        raise HTTPException(status_code=429, detail="当前 IP 访问过于频繁，请 1 小时后再试")

    verification_target = email if email else phone_number
    count_key = f"request_count:{verification_target}"
    request_count = redis_client.get(count_key)

    if request_count and int(request_count) >= settings.MAX_REQUESTS_PER_HOUR:
        log_event("send_verification_code", message=f"❌ {verification_target} 请求过于频繁", log_type="error")
        raise HTTPException(status_code=429, detail="当前账户请求过于频繁，请 1 小时后再试")

    # 2️⃣ **生成验证码**
    verification_code = generate_verification_code()
    redis_client.setex(f"verification_code:{verification_target}", settings.CODE_EXPIRE_TIME, verification_code)

    # 3️⃣ **记录请求次数**
    redis_client.incr(ip_count_key)
    redis_client.expire(ip_count_key, settings.REQUEST_LIMIT_TIME)  # 1 小时内有效

    redis_client.incr(count_key)
    redis_client.expire(count_key, settings.REQUEST_LIMIT_TIME)  # 1 小时内有效

    # 4️⃣ **发送验证码**
    if email:
        subject = "欢迎注册MBTI Compass 您的注册验证码"
        template_response = templates.TemplateResponse(
            "mail.html", {"request": request, "verification_code": verification_code}
        )
        body = template_response.body
        background_tasks.add_task(send_email, email, subject, body)
        log_event("send_verification_code", message=f"✅ {email} 验证码已发送", log_type="info")

    elif phone_number:
        background_tasks.add_task(send_sms, phone_number, verification_code)
        log_event("send_verification_code", message=f"✅ {phone_number} 短信验证码已发送", log_type="info")

    return {"message": "验证码已发送，请检查您的邮箱或短信"}


@auth_router.post("/register", response_model=TokenResponse)
async def register(user_data: RegisterRequest, db: AsyncSession = Depends(get_async_db)):
    """ ✅ 注册时验证验证码（支持邮箱或手机号） """
    email = user_data.email
    phone_number = user_data.phone_number
    username = user_data.username
    password = user_data.password
    code = user_data.verification_code

    # ✅ 必须提供用户名
    if not username:
        raise HTTPException(status_code=400, detail="用户名不能为空")

    # ✅ 必须提供邮箱或手机号
    if not email and not phone_number:
        raise HTTPException(status_code=400, detail="邮箱或手机号必须填写一个")

    # ✅ 确保验证码存在
    verification_target = email if email else phone_number
    stored_code = redis_client.get(f"verification_code:{verification_target}")

    if not stored_code:
        raise HTTPException(status_code=400, detail="验证码已过期或不存在")

    if stored_code != code:
        raise HTTPException(status_code=400, detail="验证码错误")

    async with db:
        # 检查邮箱或手机号是否已注册
        query = select(User).where(
            (User.email == email) | (User.phone_number == phone_number)
        )
        result = await db.execute(query)
        if result.scalars().first():
            raise HTTPException(status_code=400, detail="邮箱或手机号已注册")

        # 4️⃣ **创建新用户**
        hashed_password = hash_password(password)
        new_user = User(username=username, email=email, phone_number=phone_number, hashed_password=hashed_password)
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        # 删除 Redis 里的验证码
        redis_client.delete(f"verification_code:{verification_target}")

        # 5️⃣ **生成 JWT 令牌**
        access_token = create_access_token(
            {"sub": str(new_user.id)}, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        return {"access_token": access_token, "token_type": "Bearer"}



@auth_router.post("/login", response_model=TokenResponse)
async def login(user_data: LoginRequest, db: AsyncSession = Depends(get_async_db)):
    """ ✅ 用户登录 """
    email = user_data.email
    phone_number = user_data.phone_number
    password = user_data.password

    if not email and not phone_number:
        raise HTTPException(status_code=400, detail="邮箱或手机号必须填写一个")

    async with db:
        query = select(User).where(
            (User.email == email) | (User.phone_number == phone_number)
        )
        result = await db.execute(query)
        user = result.scalars().first()

    if not user:
        log_event("login", message=f"❌ 用户不存在: {email or phone_number}", log_type="error")
        raise HTTPException(status_code=400, detail="用户不存在")

    # 验证密码
    if not verify_password(password, user.hashed_password):
        log_event("login", message=f"❌ 密码错误: {email or phone_number}", log_type="error")
        raise HTTPException(status_code=400, detail="密码错误")

    # 生成 JWT 令牌
    access_token = create_access_token(
        {"sub": str(user.id)}, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    log_event("login", message=f"✅ 用户登录成功: {email or phone_number}", log_type="info")
    return {"access_token": access_token, "token_type": "Bearer"}