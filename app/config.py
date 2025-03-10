import os
from pydantic_settings import BaseSettings
from typing import ClassVar, Dict


class BaseConfig(BaseSettings):
    """ 默认环境配置 """
    # ✅ 自动从 `.env` 读取环境变量（如果没有则使用默认值）
    class Config:
        env_file = ".env"  # 允许加载 .env 文件
        extra = "allow"  # 允许额外字段

    # ✅ 运行环境（默认 development）
    ENV: str = "development"

    # ✅ JWT 配置
    JWT_SECRET_KEY: str = "HOZINWANG"  # 默认密钥
    ALGORITHM: ClassVar[str] = "HS256"  # 避免 Pydantic 解析
    ACCESS_TOKEN_EXPIRE_MINUTES:int = 3660
    # 验证码 & 频率控制
    CODE_EXPIRE_TIME:int = 600  # 5 分钟
    REQUEST_LIMIT_TIME:int = 3600  # 1 小时
    MAX_REQUESTS_PER_HOUR:int = 100  # 限制 1 小时内最多 3 次
    MAX_IP_REQUESTS_PER_HOUR:int = 100
    CODE_LENGTH:int = 6  # 验证码长度
    # 腾讯云 SMTP 配置
    SMTP_SERVER :str= "smtp.qcloudmail.com"
    SMTP_PORT :int= 465
    SMTP_USERNAME :str= "offical@sanaoll.com"
    SMTP_PASSWORD :str= "WllyXS+GM08)#"

    # ✅ MySQL 数据库配置（用于 Tortoise-ORM & SQLAlchemy）
    DB_USERNAME: str = "S1034363"
    DB_PASSWORD: str = "Aa123.com"
    DB_HOST: str = "mq.7du.pub"
    DB_PORT: int = 33789
    DB_NAME: str = "mbticompass"

    # ✅ SQLAlchemy 连接字符串
    SYNC_DATABASE_URL : str = f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    # ✅ 采用 SQLAlchemy 兼容 Async
    ASYNC_DATABASE_URL : str = f"mysql+aiomysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    # ✅ Redis 相关配置（支持 `Celery`）
    REDIS_HOST: str = "205.189.160.142"
    REDIS_PORT: int = 9736
    REDIS_DB_BROKER: int = 3  # Celery 任务队列
    REDIS_DB_RESULT: int = 4  # Celery 任务结果存储
    REDIS_PASSWORD: str = "s1034363"

    # ✅ **ai models 配置**
    DEEPSEEK_API_KEY: ClassVar[str] = "sk-52f46df1be264b35ab4d279278ae891d"
    DEEPSEEK_API_URI: ClassVar[str] = "https://api.deepseek.com"
    ALI_API_KEY: ClassVar[str] = "sk-7fd2a57774084cdab05ba07adf5f51a2"
    KIMI_APIKEY:str = "sk-ZUNT9Q0OaXKFxyFtMLgnLtiFVXPdoleE0oBvtXLdlndK0kTN"
    DOUBAO_APIKEY:str = "c804c891-89ca-408e-9e43-7d09d465f9b6"
    GEMINI_APIKEY:str = "AIzaSyDD3fH4iOlxro5T3GmMn1DEGMAHtxv3Yr8"
    XAI_APIKEY:str="xai-bF9QBXcj9xMDuQyilMrw37PVUohWT0Hn2Bjx6jpuFQx41qGvXvtnumoBDgqV53aU9TZVaePhWrOIk58X"
    BAIDU_APIKEY:str="bce-v3/ALTAK-vF32IksVvN9ahVMGJihp7/6a1d362089d241fc68e2f6e52d09bbdd0c95f5d6"
    # ✅ Redis URL（兼容 Celery & FastAPI）
    @property
    def REDIS_URL(self) -> str:
        return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/0"
    # Chrome Driver path
    LOGO_SAVE_PATH:str= "app/static/logos/"
    LOGO_S3_URL:str= "https://s2.coinmarketcap.com/static/img/coins"
    CHROME_DRIVER_PATH :str= "D:\\360Downloads\\chromedriver-win64\\chromedriver.exe"


    # ✅ Telegram 机器人通知（如果有）
    TG_TOKEN: str = ""
    TG_CHAT_ID: str = ""


# **开发环境**
class DevConfig(BaseConfig):
    DEBUG: bool = True

# **生产环境**
class ProdConfig(BaseConfig):
    DEBUG: bool = False
    REDIS_HOST: str = "prod-redis.example.com"  # 生产 Redis 服务器

# ✅ 选择配置（自动从 `.env` 读取 `ENV`）
env = os.getenv("ENV", "development")
settings = ProdConfig() if env == "production" else DevConfig()
