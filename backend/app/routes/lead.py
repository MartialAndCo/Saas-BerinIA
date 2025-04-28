from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.schemas.lead import LeadCreate, Lead
from app.models.lead import Lead as LeadModel

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/api/leads", response_model=Lead)
def create_lead(lead: LeadCreate, db: Session = Depends(get_db)):
    db_lead = LeadModel(nom=lead.nom, email=lead.email, telephone=lead.telephone, statut=lead.statut)
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead

@router.get("/api/leads", response_model=list[Lead])
def get_leads(db: Session = Depends(get_db)):
    return db.query(LeadModel).all()

@router.get("/api/leads/{lead_id}", response_model=Lead)
def get_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(LeadModel).filter(LeadModel.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    return lead
