from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class LeadBase(BaseModel):
    nom: str
    email: EmailStr
    telephone: Optional[str] = None
    entreprise: Optional[str] = None
    campagne_id: Optional[int] = None

class LeadCreate(LeadBase):
    statut: Optional[str] = "new"

class LeadUpdate(BaseModel):
    nom: Optional[str] = None
    email: Optional[EmailStr] = None
    telephone: Optional[str] = None
    entreprise: Optional[str] = None
    statut: Optional[str] = None
    campagne_id: Optional[int] = None

class Lead(LeadBase):
    id: int
    statut: str
    date_creation: datetime

    class Config:
        orm_mode = True
