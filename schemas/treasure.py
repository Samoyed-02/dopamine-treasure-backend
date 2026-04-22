from pydantic import BaseModel
from typing import Optional

class TreasureResponse(BaseModel):
    id : int
    location_name : str
    nickname : str
    treasure_type : str
    content : str
    is_claimed : bool
    image_path: Optional[str] = None

class TreasureUpdate(BaseModel):
    content: Optional[str] = None
    status: Optional[str] = None
    image_path: Optional[str] = None  # ← 추가
    
    class Config:
        from_attributes = True