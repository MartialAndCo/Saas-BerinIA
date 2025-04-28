from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.schemas.campaign import Campaign

class NicheBase(BaseModel):
    nom: str
    description: Optional[str] = None
    statut: Optional[str] = "En test"
    taux_conversion: Optional[float] = 0.0
    cout_par_lead: Optional[float] = 0.0
    recommandation: Optional[str] = "Continuer"

class NicheCreate(NicheBase):
    pass

class NicheUpdate(NicheBase):
    nom: Optional[str] = None

class NicheResponse(NicheBase):
    id: int
    date_creation: Optional[datetime] = None
    campagnes: List[Campaign] = []
    leads: List = []
    
    class Config:
        from_attributes = True
