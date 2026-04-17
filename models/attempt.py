from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
import datetime

class Attempt(Base):
    __tablename__ = "attempts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    student_id = Column(String(100))
    department = Column(String(100))
    location_id = Column(Integer, ForeignKey("locations.id"))
    mission_type = Column(String(20))
    answer = Column(String(100))
    image_path = Column(String(500), nullable=True)
    is_correct = Column(Boolean, default=False)
    status = Column(String(20), default="pending")
    attempt_time = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    phone = Column(String(50), nullable = True)
    agreed = Column(Boolean, default=False)
