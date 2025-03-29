from app.core.logger import log_event
async def send_sms(phone_number: str, verification_code: str):
    """ 发送短信验证码 """
    try:
        # 这里调用你的短信 API，比如 Twilio / 腾讯云短信服务
        sms_content = f"您的验证码是 {verification_code}，10 分钟内有效。"
        # send_sms_api(phone_number, sms_content)  # 替换为实际的短信发送逻辑
        log_event("send_sms", message=f"✅ 短信验证码已发送到 {phone_number}", log_type="info")
    except Exception as e:
        log_event("send_sms", message=f"❌ 短信发送失败: {e}", log_type="error")