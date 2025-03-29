from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.base import get_async_db
from app.models.user_model import User, UserRole
from datetime import timedelta, datetime, timezone
from jose import JWTError, jwt
from passlib.hash import pbkdf2_sha256  # ✅ 使用 pbkdf2_sha256 替代 bcrypt
from app.config import settings
from fastapi.security import OAuth2PasswordBearer
from fastapi import Security

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")  # tokenUrl 只是文档用，写对就行

# 🔹 JWT 配置
SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = 43200  # 30 天有效期（适合 App）

def hash_password(password: str) -> str:
    """ ✅ 使用 PBKDF2-SHA256 进行密码哈希 """
    return pbkdf2_sha256.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """ ✅ 校验密码 """
    return pbkdf2_sha256.verify(plain_password, hashed_password)

# async def get_current_user(token: str, db: AsyncSession = Depends(get_async_db)) -> User:
async def get_current_user(
            token: str = Security(oauth2_scheme),
            db: AsyncSession = Depends(get_async_db)
    ) -> User:
    """ ✅ 获取当前登录用户（检查 JWT 令牌） """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))

        # 🔹 检查 JWT 是否过期
        exp = payload.get("exp")
        if exp and datetime.now(timezone.utc).timestamp() > exp:
            raise HTTPException(status_code=401, detail="令牌已过期")

        # 🔹 查询用户信息
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()

        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="用户未登录或已注销")

        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="无效令牌")

async def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """ ✅ 仅管理员可操作 """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="无管理员权限")
    return current_user

def create_access_token(data: dict, expires_delta: timedelta):
    """ ✅ 生成 JWT 令牌 """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta  # ✅ 使用 `datetime.now(timezone.utc)`
    to_encode.update({"exp": expire.timestamp()})  # ✅ `exp` 存储时间戳
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
