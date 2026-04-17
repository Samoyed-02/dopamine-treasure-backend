from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
import os
import models.location as models
import models.treasure as treasure_models
import models.attempt as attempt_models
import schemas.location as schemas
import schemas.attempt as attempt_schemas
import schemas.treasure as treasure_schemas
from typing import Optional
from sqlalchemy import func
import models.attempt as attempt_models

router = APIRouter()

# 장소별 보물 현황
@router.get("/admin/locations")
def admin_locations(db: Session = Depends(get_db)):
    locations = db.query(models.Location).all()
    return locations

# 보물 전체 목록
@router.get("/admin/treasures")
def admin_treasures(page: int = 1, status: Optional[str] = None, db: Session = Depends(get_db)):
    size = 10
    offset = (page - 1) * size
    
    query = db.query(treasure_models.Treasure)
    
    if status:
        query = query.filter(treasure_models.Treasure.status == status)
    
    total = query.count()
    treasures = query.offset(offset).limit(size).all()

    result = []
    for t in treasures:
        # 해당 학번의 보물 획득 개수 조회
        claimed_count = db.query(treasure_models.Treasure).filter(
            treasure_models.Treasure.claimed_by == t.student_id
        ).count()
        location = db.query(models.Location).filter(
            models.Location.id == t.location_id
            ).first()

        result.append({
            "id": t.id,
            "location_id": t.location_id,
            "name": t.name,
            "student_id": t.student_id,
            "department": t.department,
            "treasure_type": t.treasure_type,
            "content": t.content,
            "is_claimed": t.is_claimed,
            "status": t.status,
            "image_path": t.image_path,
            "claimed_count": claimed_count,
            "location_name": location.name if location else None,
            "mission_content": t.mission_content if location else None,
            "mission_answer": t.mission_answer
        })
    
    return {"total": total, "page": page, "size": size, "treasures": result}
# 사진 미션 승인 대기 목록
@router.get("/admin/attempts")
def admin_attempts(db: Session = Depends(get_db)):
    attempts = db.query(attempt_models.Attempt).filter(
        attempt_models.Attempt.status == "pending"
    ).all()

    result = []
    for a in attempts:
        claimed_count = db.query(treasure_models.Treasure).filter(
            treasure_models.Treasure.claimed_by == a.student_id
        ).count()

        result.append({
            "id": a.id,
            "name": a.name,
            "student_id": a.student_id,
            "department": a.department,
            "phone": a.phone,          # 추가
            "location_id": a.location_id,
            "image_path": a.image_path,
            "status": a.status,
            "claimed_count": claimed_count  # 추가
        })

    return {"attempts": result}

# 사진 미션 승인/거절
@router.patch("/admin/attempts/{attempt_id}")
def approve_attempt(attempt_id: int, request: attempt_schemas.AttemptApprove, db: Session = Depends(get_db)):
    attempt = db.query(attempt_models.Attempt).filter(
        attempt_models.Attempt.id == attempt_id
    ).first()

    if not attempt:
        return {"success": False, "message": "해당 인증 기록이 없어요!"}

    attempt.status = request.status
    if request.status == "approved":
        attempt.is_correct = True

    db.commit()
    db.refresh(attempt)

    return {"success": True, "message": "처리 완료!"}

# 미션/정답 수정
@router.patch("/admin/locations/{location_id}")
def fix_location(location_id: int, request: schemas.LocationUpdate, db: Session = Depends(get_db)):
    location = db.query(models.Location).filter(models.Location.id == location_id).first()

    db.commit()
    db.refresh(location)

    return {"success": True, "message": "수정 완료!"}

# 응원메세지 수정
@router.patch("/admin/treasures/{treasure_id}")
def fix_treasure(treasure_id: int, request: treasure_schemas.TreasureUpdate, db: Session = Depends(get_db)):
    treasure = db.query(treasure_models.Treasure).filter(
        treasure_models.Treasure.id == treasure_id
    ).first()

    if not treasure:
        return {"success": False, "message": "해당 보물이 없어요!"}

    treasure.content = request.content

    db.commit()
    db.refresh(treasure)

    return {"success": True, "message": "수정 완료!"}

@router.post("/admin/login")
def admin_login(password: str, db: Session = Depends(get_db)):
    admin_password = os.getenv("ADMIN_PASSWORD")

    if password != admin_password:
        return {"success": False, "message": "비밀번호가 틀렸어요!"}
    
    return{"success": True, "message": "관리자 승인 완료!"}
    
@router.get("/admin/claims")
def admin_claims(db: Session = Depends(get_db)):
    treasures = db.query(treasure_models.Treasure).filter(
        treasure_models.Treasure.is_claimed == True
    ).order_by(treasure_models.Treasure.claimed_at.desc()).all()  # 여기로 이동
    
    result = []
    for t in treasures:
        location = db.query(models.Location).filter(
            models.Location.id == t.location_id  # 장소 조회로 수정
        ).first()
        result.append({
            "id": t.id,
            "location_name": location.name if location else None,
            "treasure_type": t.treasure_type,
            "content": t.content,
            "claimed_by": t.claimed_by,
            "claimed_at": t.claimed_at
        })
    
    return {"claims": result}

from sqlalchemy import func

@router.get("/admin/stats")
def admin_stats(db: Session = Depends(get_db)):
    results = db.query(
        treasure_models.Treasure.claimed_by,
        func.count(treasure_models.Treasure.id).label("claimed_count")
    ).filter(
        treasure_models.Treasure.is_claimed == True
    ).group_by(
        treasure_models.Treasure.claimed_by
    ).all()

    stats = []
    for r in results:
        attempt = db.query(attempt_models.Attempt).filter(
            attempt_models.Attempt.student_id == r.claimed_by
        ).first()
        stats.append({
            "student_id": r.claimed_by,
            "name": attempt.name if attempt else None,
            "department": attempt.department if attempt else None,
            "claimed_count": r.claimed_count
        })

    return {"stats": stats}