from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
import models.location as models
import models.treasure as treasure_models
import schemas.location as schemas
import models.attempt as attempt_models

router = APIRouter()

# 장소 목록 전체 조회
@router.get("/locations")
def get_locations(db: Session = Depends(get_db)):
    locations = db.query(models.Location).all()
    
    result = []
    for l in locations:
        # pending attempt가 있는 장소는 개수에서 제외
        pending_attempt = db.query(attempt_models.Attempt).filter(
            attempt_models.Attempt.location_id == l.id,
            attempt_models.Attempt.status == "pending"
        ).first()

        if pending_attempt:
            treasure_count = 0  # pending 중이면 0으로 표시
        else:
            treasure_count = db.query(treasure_models.Treasure).filter(
                treasure_models.Treasure.location_id == l.id,
                treasure_models.Treasure.status == "approved",
                treasure_models.Treasure.is_claimed == False
            ).count()
        
        result.append({
            "id": l.id,
            "name": l.name,
            "treasure_count": treasure_count,
            "max_count": 10
        })
    
    return result
# 특정 장소 조회
@router.get("/locations/{location_id}")
def get_location(location_id: int, student_id: str = None, db: Session = Depends(get_db)):
    location = db.query(models.Location).filter(
        models.Location.id == location_id
    ).first()

    # 해당 장소에 pending attempt가 있으면 보물 없는 것처럼 처리
    pending_attempt = db.query(attempt_models.Attempt).filter(
        attempt_models.Attempt.location_id == location_id,
        attempt_models.Attempt.status == "pending"
    ).first()

    if pending_attempt:
        treasure = None
    else:
        query = db.query(treasure_models.Treasure).filter(
            treasure_models.Treasure.location_id == location_id,
            treasure_models.Treasure.is_claimed == False,
            treasure_models.Treasure.status == "approved"
        )

        if student_id:
            query = query.filter(treasure_models.Treasure.student_id != student_id)

        treasure = query.first()

    own_treasure = db.query(treasure_models.Treasure).filter(
    treasure_models.Treasure.location_id == location_id,
    treasure_models.Treasure.is_claimed == False,
    treasure_models.Treasure.status == "approved",
    treasure_models.Treasure.student_id == str(student_id)
    ).first() if student_id else None

    return {
        "id": location.id,
        "name": location.name,
        "mission_type": treasure.mission_type if treasure else None,
        "mission_content": treasure.mission_content if treasure else None,
        "treasure_count": db.query(treasure_models.Treasure).filter(
            treasure_models.Treasure.location_id == location_id,
            treasure_models.Treasure.is_claimed == False,
            treasure_models.Treasure.status == "approved"
        ).count(),
        "is_own": own_treasure is not None
    }