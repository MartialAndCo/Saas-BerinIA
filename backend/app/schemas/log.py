from pydantic import BaseModel
from datetime import datetime

class LogResponse(BaseModel):
    id: int
    type: str
    message: str
    timestamp: datetime

    class Config:
        from_attributes = True
        orm_mode = True
