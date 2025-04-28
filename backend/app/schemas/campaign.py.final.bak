from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class CampaignBase(BaseModel):
    nom: str
    description: Optional[str] = None
    niche_id: int
    target_leads: Optional[int] = 0
    agent: Optional[str] = None

class CampaignCreate(CampaignBase):
    pass

class CampaignUpdate(BaseModel):
    nom: Optional[str] = None
    description: Optional[str] = None
    statut: Optional[str] = None
    niche_id: Optional[int] = None
    target_leads: Optional[int] = None
    agent: Optional[str] = None

class Campaign(CampaignBase):
    id: int
    statut: str
    date_creation: datetime
    leads: Optional[int] = 0
    conversion: Optional[float] = 0
    progress: Optional[int] = 0

    class Config:
        orm_mode = True
