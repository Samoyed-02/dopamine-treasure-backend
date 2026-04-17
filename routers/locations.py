from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
import models.location as models
import schemas.location as schemas

router = APIRouter()

# 장소 목록 전체 조회
@router.get("/locations")
def get_locations(db: Session = Depends(get_db)):
    locations = db.query(models.Location).all()
    return locations

#특정 장소 조회
@router.get("/locations/{location_id}")
def get_location(location_id: int, db: Session = Depends(get_db)):
    location = db.query(models.Location).filter(models.Location.id == location_id).first()
    return location
    