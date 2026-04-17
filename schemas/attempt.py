from pydantic import BaseModel
from typing import Optional

class AttemptRequest(BaseModel):
    name: str
    student_id: str
    department: str
    mission_type: str
    answer : Optional[str] = None

class AttemptResponse(BaseModel):
    is_correct : bool
    message : str
    status: Optional[str] = None

class AttemptApprove(BaseModel):
    status: str

    class Config:
        from_attributes = True
    