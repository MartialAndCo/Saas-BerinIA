from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class AgentLogBase(BaseModel):
    operation: str
    status: str
    execution_time: float

class AgentLogCreate(AgentLogBase):
    agent_id: int
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None

class AgentLogFeedback(BaseModel):
    score: float
    text: Optional[str] = None
    source: str = "human"
    validated: bool = True

class AgentLogUpdate(BaseModel):
    status: Optional[str] = None
    feedback_score: Optional[float] = None
    feedback_text: Optional[str] = None
    feedback_source: Optional[str] = None
    feedback_validated: Optional[bool] = None

class AgentLog(AgentLogBase):
    id: int
    agent_id: int
    timestamp: datetime
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    feedback_score: Optional[float] = None
    feedback_text: Optional[str] = None
    feedback_source: Optional[str] = None
    feedback_timestamp: Optional[datetime] = None
    feedback_validated: bool = False

    class Config:
        orm_mode = True
