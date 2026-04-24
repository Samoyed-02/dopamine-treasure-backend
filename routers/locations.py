from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
import models.location as models
import models.treasure as treasure_models
import models.attempt as attempt_models

router = APIRouter()

# 장소 목록 전체 조회
@router.get("/locations")
def get_locations(db: Session = Depends(get_db)):
    locations = db.query(models.Location).all()
    result = []
    for l in locations:
        # pending 중인 photo 보물 제외하고 카운트
        pending_attempt_location_ids = [
            a.location_id for a in db.query(attempt_models.Attempt).filter(
                attempt_models.Attempt.location_id == l.id,
                attempt_models.Attempt.status == "pending"
            ).all()
        ]

        query = db.query(treasure_models.Treasure).filter(
            treasure_models.Treasure.location_id == l.id,
            treasure_models.Treasure.status == "approved",
            treasure_models.Treasure.is_claimed == False
        )

        if pending_attempt_location_ids:
            query = query.filter(treasure_models.Treasure.mission_type != "photo")

        result.append({
            "id": l.id,
            "name": l.name,
            "treasure_count": query.count(),
            "max_count": 10
        })
    return result


# 특정 장소 조회
@router.get("/locations/{location_id}")
def get_location(location_id: int, student_id: str = None, db: Session = Depends(get_db)):
    location = db.query(models.Location).filter(
        models.Location.id == location_id
    ).first()

    # 기본 보물 쿼리
    query = db.query(treasure_models.Treasure).filter(
        treasure_models.Treasure.location_id == location_id,
        treasure_models.Treasure.is_claimed == False,
        treasure_models.Treasure.status == "approved"
    )

    # 전체 기준 — pending 중인 photo 보물 제외 (모든 사용자에게)
    has_pending = db.query(attempt_models.Attempt).filter(
        attempt_models.Attempt.location_id == location_id,
        attempt_models.Attempt.status == "pending"
    ).first() is not None

    if has_pending:
        query = query.filter(treasure_models.Treasure.mission_type != "photo")

    # 본인 보물 제외 + 본인 pending 시 photo 차단
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
        "treasure_count": query.count(),
        "is_own": own_treasure is not None
    }