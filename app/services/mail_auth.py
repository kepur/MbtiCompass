from app.core.logger import log_event
from app.config import settings
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiosmtplib

async def send_email(recipient: str, subject: str, body: str):
    """ 发送邮件 """
    msg = MIMEMultipart()
    msg["From"] = settings.SMTP_USERNAME
    msg["To"] = recipient
    msg["Subject"] = subject
    # msg.attach(MIMEText(body, "plain", "utf-8"))
    msg.attach(MIMEText(body, "html", "utf-8"))  # ✅ 这里必须用 "html"

    try:
        await aiosmtplib.send(
            msg,
            hostname=settings.SMTP_SERVER,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USERNAME,
            password=settings.SMTP_PASSWORD,
            use_tls=True,
        )
        log_event("send_email", message=f"✅ 邮件已发送: {recipient}", log_type="info")
    except Exception as e:
        log_event("send_email", message=f"❌ 发送失败: {e}", log_type="error")