from pydantic import BaseModel

class LocationResponse(BaseModel):
    id : int
    name : str
    mission_content : str
    treasure_count : int
    
class LocationUpdate(BaseModel):
    mission_content: str
    mission_answer: str

    class Config:
        from_attributes = True

