from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .database import get_db
from .models import UserLocation
from datetime import datetime

router = APIRouter()

@router.post("/update-location/")
def update_user_location(user_id: int, latitude: float, longitude: float, country: str, city: str, address: str, db: Session = Depends(get_db)):
    """
    更新用户的地理位置，每 1 小时调用一次
    """
    user_location = db.query(UserLocation).filter(UserLocation.user_id == user_id).first()

    if user_location:
        user_location.latitude = latitude
        user_location.longitude = longitude
        user_location.country = country
        user_location.city = city
        user_location.address = address
        user_location.updated_at = datetime.utcnow()
    else:
        new_location = UserLocation(
            user_id=user_id,
            latitude=latitude,
            longitude=longitude,
            country=country,
            city=city,
            address=address
        )
        db.add(new_location)

    db.commit()
    return {"status": "success"}
