from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from app.models import get_db
from app.models import UserLocation,EventLocation
from app.utils import haversine  # 引入 Haversine 计算函数

router = APIRouter()

@router.get("/nearby-users/")
def get_nearby_users(user_lat: float, user_lon: float, radius_km: float = 5, db: Session = Depends(get_db)):
    """
    获取附近的用户（5km 范围内）
    """
    users = db.query(UserLocation).all()
    nearby_users = [
        user for user in users if haversine(user_lat, user_lon, user.latitude, user.longitude) <= radius_km
    ]
    return {"nearby_users": nearby_users}


@router.get("/nearby-events/")
def get_nearby_events(user_lat: float, user_lon: float, radius_km: float = 10, db: Session = Depends(get_db)):
    """
    获取附近的活动（10km 范围内）
    """
    events = db.query(EventLocation).all()
    nearby_events = [
        event for event in events if haversine(user_lat, user_lon, event.latitude, event.longitude) <= radius_km
    ]
    return {"nearby_events": nearby_events}