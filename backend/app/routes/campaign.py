from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.schemas.campaign import CampaignCreate, Campaign
from app.models.campaign import Campaign as CampaignModel

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/api/campaigns", response_model=Campaign)
def create_campaign(campaign: CampaignCreate, db: Session = Depends(get_db)):
    db_campaign = CampaignModel(nom=campaign.nom, description=campaign.description, statut=campaign.statut)
    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign)
    return db_campaign

@router.get("/api/campaigns", response_model=list[Campaign])
def get_campaigns(db: Session = Depends(get_db)):
    return db.query(CampaignModel).all()
