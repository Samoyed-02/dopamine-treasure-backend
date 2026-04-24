from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from pydantic import BaseModel
import models.treasure as models
import models.location as location_models
import models.attempt as attempt_models
import datetime
import random
import os
import uuid

router = APIRouter()


# ─── 보물 등록 ─────────────────────────────────────────────────
@router.post("/treasures")
async def create_treasure(
    name: str = Form(...),
    student_id: str = Form(...),
    department: str = Form(...),
    location_id: int = Form(...),
    treasure_type: str = Form(...),
    mission_type: str = Form(...),
    mission_content: str = Form(...),
    content: Optional[str] = Form(None),
    mission_answer: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    image: UploadFile = File(None)
):
    treasure_count = db.query(models.Treasure).filter(
        models.Treasure.location_id == location_id,
        models.Treasure.status == "approved"
    ).count()

    if treasure_count >= 10:
        return {"success": False, "message": "해당 장소는 보물이 가득 찼어요! 다른 장소를 선택해주세요."}

    image_path = None
    if treasure_type in ["gifticon", "meme"] and image and image.filename:
        ext = os.path.splitext(image.filename)[1]
        image_path = f"uploads/{uuid.uuid4()}{ext}"
        with open(image_path, "wb") as f:
            f.write(await image.read())

    treasure = models.Treasure(
        name=name,
        student_id=student_id,
        department=department,
        location_id=location_id,
        treasure_type=treasure_type,
        mission_type=mission_type,
        mission_content=mission_content,
        content=content,
        mission_answer=mission_answer,
        image_path=image_path,
        is_claimed=False,
        status="pending"
    )

    db.add(treasure)
    db.commit()
    db.refresh(treasure)

    return {"success": True, "message": "보물을 숨겼어요! 🎁"}


# ─── 미션 제출 ─────────────────────────────────────────────────
@router.post("/locations/{location_id}/verify")
async def verify_mission(
    location_id: int,
    name: str = Form(...),
    student_id: str = Form(...),
    department: str = Form(...),
    mission_type: str = Form(...),
    phone: Optional[str] = Form(None),
    agreed: bool = Form(False),
    answer: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    image: UploadFile = File(None)
):
    # pending 중이면 시간 상관없이 차단
    pending_attempt = db.query(attempt_models.Attempt).filter(
        attempt_models.Attempt.student_id == student_id,
        attempt_models.Attempt.status == "pending"
    ).first()

    if pending_attempt:
        return {"success": False, "message": "사진 미션 승인 대기 중이에요!"}

    # 승인된 경우 30분 제한
    one_hour_ago = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=0.5)
    recent_attempt = db.query(attempt_models.Attempt).filter(
        attempt_models.Attempt.student_id == student_id,
        attempt_models.Attempt.is_correct == True,
        attempt_models.Attempt.attempt_time >= one_hour_ago
    ).first()

    if recent_attempt:
        return {"success": False, "message": "30분 후에 다시 도전해보세요!"}

    # ─── 퀴즈 미션 ───
    if mission_type == "quiz":
        treasure = db.query(models.Treasure).filter(
            models.Treasure.location_id == location_id,
            models.Treasure.is_claimed == False,
            models.Treasure.status == "approved",
            models.Treasure.mission_type == "quiz",
            models.Treasure.student_id != student_id,
            models.Treasure.mission_answer != None
        ).first()

        if not treasure:
            return {"success": False, "message": "보물이 없어요!"}

        answers = [a.strip() for a in treasure.mission_answer.split(",")]
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

    # ─── 사진 미션 ───
    if mission_type == "photo" and image and image.filename:
        available = db.query(models.Treasure).filter(
            models.Treasure.location_id == location_id,
            models.Treasure.is_claimed == False,
            models.Treasure.status == "approved",
            models.Treasure.student_id != student_id
        ).first()

        if not available:
            return {"success": False, "message": "획득 가능한 보물이 없어요!"}

        ext = os.path.splitext(image.filename)[1]
        image_path = f"uploads/{uuid.uuid4()}{ext}"
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

    return {"success": False, "message": "사진을 첨부해주세요!"}


# ─── 보물 획득 ─────────────────────────────────────────────────
class ClaimRequest(BaseModel):
    student_id: str

@router.post("/locations/{location_id}/claim")
def claim_treasure(
    location_id: int,
    request: ClaimRequest,
    db: Session = Depends(get_db)
):
    student_id = request.student_id

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


# ─── 사진 미션 pending 여부 확인 ───────────────────────────────
@router.get("/my-pending")
def my_pending(student_id: str, db: Session = Depends(get_db)):
    pending = db.query(attempt_models.Attempt).filter(
        attempt_models.Attempt.student_id == student_id,
        attempt_models.Attempt.status == "pending"
    ).first()
    return {"pending": pending is not None}