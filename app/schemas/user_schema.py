from pydantic import BaseModel, EmailStr,field_validator,model_validator
from typing import Optional
from datetime import datetime
from pydantic_core.core_schema import ValidationInfo
from pydantic import BaseModel, EmailStr, constr, Field, validator
from app.core.logger import log_event

class SendVerificationCodeRequest(BaseModel):
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = Field(None, min_length=10, max_length=15)

    @model_validator(mode="before")
    @classmethod
    def check_email_or_phone(cls, values):
        email = values.get("email")
        phone_number = values.get("phone_number")

        if not email and not phone_number:
            log_event("send_verification_code", message="❌ 用户未提供邮箱或手机号", log_type="error")
            raise ValueError("邮箱或手机号必须填写一个")

        log_event("send_verification_code", message=f"✅ 用户请求验证码: {email or phone_number}", log_type="info")
        return values

class RegisterRequest(BaseModel):
    """ ✅ 用户注册请求体 """
    username: str = Field(..., min_length=5, max_length=20)
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None  # ✅ 统一名称，之前是 `phone`
    password: str
    verification_code: str

    @field_validator("email", mode="before")
    @classmethod
    def check_email(cls, value, info: ValidationInfo):
        """ ✅ 确保至少填写 email 或 phone_number """
        phone_number = info.data.get("phone_number")  # ✅ 统一名称

        if not value and not phone_number:
            raise ValueError("邮箱和手机号至少提供一个")
        return value

    @field_validator("phone_number", mode="before")  # ✅ 统一名称
    @classmethod
    def check_phone(cls, value, info: ValidationInfo):
        """ ✅ 确保至少填写 email 或 phone_number """
        email = info.data.get("email")

        if not value and not email:
            raise ValueError("邮箱和手机号至少提供一个")
        return value

class LoginRequest(BaseModel):
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    password: str = Field(..., min_length=6, max_length=20)

    @classmethod
    @field_validator("email", "phone_number", mode="before")
    def check_email_or_phone(cls, value, info):
        email = info.data.get("email")
        phone_number = info.data.get("phone_number")

        if not email and not phone_number:
            raise ValueError("邮箱或手机号必须填写一个")
        return value

# ✅ JWT 令牌返回模型
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"

# ✅ 用户创建请求模型（支持手机号 & 邮箱）
class UserCreate(BaseModel):
    email: Optional[EmailStr] = None  # 允许为空（如果用户用手机号注册）
    phone_number: Optional[str] = None  # 允许为空（如果用户用邮箱注册）
    username: str
    password: str

# ✅ 用户更新请求模型（用户只能改自己的信息）
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: Optional[str] = None

# ✅ 用户登录请求模型
class UserLogin(BaseModel):
    login: str  # 用户可以输入邮箱或手机号
    password: str

# ✅ 用户响应模型
class UserResponse(BaseModel):
    id: int
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    birthday: Optional[datetime] = None
    gender: Optional[str] = None
    zodiac_sign: Optional[str] = None
    bazi:Optional[str] = None
    wuxing: Optional[str] = None
    username: str
    created_at: datetime


    class Config:
        from_attributes = True
