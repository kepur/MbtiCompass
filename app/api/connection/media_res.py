from fastapi import APIRouter,Depends,HTTPException,Request
from app.config import settings
from app.models.post_model import PostVideo,PostAudio,PostImage
from app.models.base import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import hash_password,get_current_user, get_admin_user
from sqlalchemy.future import select
from app.models.user_model import User, UserRole

media_router = APIRouter(prefix="/media", tags=["Media"])

'''
请求服务器:video_id 
返回:
{
	"mc":"asdfasdfasdfasdfasdf"
	"ms":"proxy.sanaoll.com"
	"du":"http://127.0.0.1:1992/mbticompass/decode/"
	"h":1
}
'''
@media_router.get("/vod/{v_id}")
async def get_video_media_with_id(
    v_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    async with db:
        result = await db.execute(select(PostVideo).where(PostVideo.id == v_id))
        video = result.scalars().first()
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")

        _resp = {
            "mc": video.media_code,  # 假设 media_code 是视频的唯一标识
            "ms": settings.MEDIA_SERVER,
            "du": settings.MEDIA_DECODER_SERVER,
            "h": video.definition #是否支持高清
        }
        return _resp

@media_router.post("/vcl")
def get_voice_media():
    pass

@media_router.post("/img")
def get_img_media():
    pass
