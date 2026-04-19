from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from sqlalchemy import or_
import models.treasure as models
import models.location as location_models
import models.attempt as attempt_models
import schemas.treasure as treasure_schemas
import schemas.attempt as attempt_schemas
import datetime
import random

router = APIRouter()

# 보물 등록
 
# 미션 제출
@router.post("/locations/{location_id}/verify")
async def verify_mission(
    location_id: int,
    name: str,
    student_id: str,
    department: str,
    mission_type: str,
    phone: Optional[str] = None,
    agreed: bool = False,
    answer: Optional[str] = None,
    db: Session = Depends(get_db),
    image: UploadFile = File(None)
):
    # 1시간 제한 체크
    one_hour_ago = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=0.5)
    recent_attempt = db.query(attempt_models.Attempt).filter(
        attempt_models.Attempt.student_id == student_id,
        or_(attempt_models.Attempt.is_correct == True,
            attempt_models.Attempt.status == "pending"
        ),
        attempt_models.Attempt.attempt_time >= one_hour_ago
    ).first()

    if recent_attempt:
        return {"success": False, "message": "30분후에 다시 도전해보세요!"}

    # 퀴즈 미션
    if mission_type == "quiz":
        location = db.query(location_models.Location).filter(
            models.Treasure.location_id == location_id,
            models.Treasure.is_claimed == False,
            models.Treasure.status == "approved"
        ).first()

        answers = [a.strip() for a in location.mission_answer.split(",")]
        is_correct = answer.strip() in answers

        attempt = attempt_models.Attempt(
            name=name,
            student_id=student_id,
            department=department,
            location_id=location_id,
            mission_type="quiz",
            answer=answer,
            is_correct=is_correct,
            status="approved" if is_correct else "rejected"
        )

        db.add(attempt)
        db.commit()

        if is_correct:
            return {"success": True, "message": "인증 성공!"}
        else:
            return {"success": False, "message": "정답이 아니에요. 다시 도전해보세요!"}

    # 사진 미션
    if mission_type == "photo" and image and image.filename:
        import os
        import uuid
        ext = os.path.splitext(image.filename)[1]  # 확장자 추출
        unique_filename = f"{uuid.uuid4()}{ext}"   # 고유 파일명 생성
        image_path = f"uploads/{unique_filename}"
        with open(image_path, "wb") as f:
            f.write(await image.read())

        attempt = attempt_models.Attempt(
            name=name,
            student_id=student_id,
            department=department,
            location_id=location_id,
            phone=phone,
            agreed=agreed,
            mission_type="photo",
            image_path=image_path,
            is_correct=False,
            status="pending"
        )

        db.add(attempt)
        db.commit()

        return {"success": True, "message": "사진이 제출됐어요! 관리자 승인 후 보물을 획득할 수 있어요 🎁"}
    
    return{"success": False, "message": "사진을 첨부해주세요!"}


# 보물 획득
@router.post("/locations/{location_id}/claim")
def claim_treasure(location_id: int, student_id: str, db: Session = Depends(get_db)):
    treasures = db.query(models.Treasure).filter(
        models.Treasure.location_id == location_id,
        models.Treasure.is_claimed == False,
        models.Treasure.student_id != student_id,
        models.Treasure.status == "approved"
    ).all()

    if not treasures:
        return {"success": False, "message": "보물이 없어요!"}

    treasure = random.choice(treasures)

    treasure.is_claimed = True
    treasure.claimed_by = student_id
    treasure.claimed_at = datetime.datetime.now(datetime.timezone.utc)
    db.commit()
    db.refresh(treasure)

    return {
        "success": True,
        "treasure": {
            "type": treasure.treasure_type,
            "content": treasure.content,
            "image_path": treasure.image_path
        }
    }