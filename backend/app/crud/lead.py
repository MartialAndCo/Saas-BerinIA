from sqlalchemy.orm import Session
from app.models.lead import Lead
from app.schemas.lead import LeadCreate

def create_lead(db: Session, lead: LeadCreate) -> Lead:
    db_lead = Lead(
        nom=lead.nom,
        email=lead.email,
        telephone=lead.telephone,
        statut=lead.statut,
        campagne_id=lead.campagne_id
    )
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead

def get_leads(db: Session):
    return db.query(Lead).all()
