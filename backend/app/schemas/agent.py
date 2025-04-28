from pydantic import BaseModel
from typing import Optional, Dict, List, Any, Union
from datetime import datetime

class AgentBase(BaseModel):
    nom: str
    type: str
    statut: Optional[str] = "inactive"

class AgentCreate(AgentBase):
    configuration: Optional[Dict[str, Any]] = None
    prompt_template: Optional[str] = None
    log_level: Optional[str] = "INFO"

class AgentUpdate(BaseModel):
    nom: Optional[str] = None
    type: Optional[str] = None
    statut: Optional[str] = None
    configuration: Optional[Dict[str, Any]] = None
    prompt_template: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None
    dependencies: Optional[Dict[str, Any]] = None
    log_level: Optional[str] = None
    feedback_score: Optional[float] = None
    last_feedback_date: Optional[datetime] = None

class Agent(AgentBase):
    id: int
    derniere_execution: Optional[datetime] = None
    leads_generes: int = 0
    campagnes_actives: int = 0
    date_creation: datetime
    configuration: Optional[Dict[str, Any]] = None
    prompt_template: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None
    dependencies: Optional[Dict[str, Any]] = None
    log_level: Optional[str] = "INFO"
    feedback_score: Optional[float] = 0.0
    last_feedback_date: Optional[datetime] = None

    class Config:
        orm_mode = True
