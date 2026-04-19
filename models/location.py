from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
import datetime

class Location(Base):
    __tablename__= "locations"

    id = Column(Integer, primary_key = True, index=True)
    name = Column(String(100))
  
