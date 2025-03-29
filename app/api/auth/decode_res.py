from fastapi import APIRouter, HTTPException
from starlette.responses import Response
import hmac, hashlib
from app.config import settings

decode_router = APIRouter(prefix="/mbticompass", tags=["decode"])

@decode_router.get("/decode/{token}")
def get_key(token: str):
    try:
        key = hmac.new(settings.MEDIA_SECRET_KEY.encode(), token.encode(), hashlib.sha256).digest()[:16]
        return Response(content=key, media_type="application/octet-stream")
    except Exception:
        raise HTTPException(status_code=404, detail="Invalid token")
