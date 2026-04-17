from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
import datetime

class Treasure(Base):
    __tablename__ = "treasures"

    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"))
    name = Column(String(100))
    student_id = Column(String(100))
    department = Column(String(100))
    treasure_type = Column(String(20))
    content = Column(String(1000))
    is_claimed = Column(Boolean, default=False)
    image_path = Column(String(500), nullable=True)
    status = Column(String(20), default="pending")
    claimed_by = Column(String(100), nullable=True)   # 획득자 학번
    claimed_at = Column(DateTime, nullable=True)       # 획득 시간
    mission_content = Column(String(500))
    mission_answer = Column(String(100))
    mission_type = Column(String(20))  # "quiz" or "photo"