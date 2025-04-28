from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.api import deps
from app.models.lead import Lead as LeadModel
from app.schemas.lead import Lead, LeadCreate, LeadUpdate

# Remplacer
router = APIRouter(tags=["Leads"])

@router.get("/", response_model=List[Lead])
def get_leads(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    search: Optional[str] = Query(None),
    statut: Optional[str] = Query(None),
    campagne_id: Optional[int] = Query(None),
    db: Session = Depends(deps.get_db)
):
    """
    Récupère la liste des leads avec filtres optionnels
    """
    # Construire la requête de base
    query = db.query(LeadModel)
    
    # Appliquer les filtres
    if search:
        query = query.filter(
            (LeadModel.nom.ilike(f"%{search}%")) | 
            (LeadModel.email.ilike(f"%{search}%")) |
            (LeadModel.telephone.ilike(f"%{search}%"))
        )
    
    if statut:
        query = query.filter(LeadModel.statut == statut)
    
    if campagne_id:
        query = query.filter(LeadModel.campagne_id == campagne_id)
    
    # Exécuter la requête avec pagination
    leads = query.offset(skip).limit(limit).all()
    return leads

@router.post("/", response_model=Lead, status_code=status.HTTP_201_CREATED)
def create_lead(lead: LeadCreate, db: Session = Depends(deps.get_db)):
    """
    Crée un nouveau lead
    """
    db_lead = LeadModel(
        nom=lead.nom,
        email=lead.email,
        telephone=lead.telephone,
        entreprise=lead.entreprise,
        statut=lead.statut,
        campagne_id=lead.campagne_id
    )
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead

@router.get("/{lead_id}", response_model=Lead)
def get_lead(lead_id: int, db: Session = Depends(deps.get_db)):
    """
    Récupère un lead spécifique par son ID
    """
    lead = db.query(LeadModel).filter(LeadModel.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead

@router.put("/{lead_id}", response_model=Lead)
def update_lead(lead_id: int, lead: LeadUpdate, db: Session = Depends(deps.get_db)):
    """
    Met à jour un lead existant
    """
    db_lead = db.query(LeadModel).filter(LeadModel.id == lead_id).first()
    if not db_lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    update_data = lead.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_lead, key, value)
    
    db.commit()
    db.refresh(db_lead)
    return db_lead

@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lead(lead_id: int, db: Session = Depends(deps.get_db)):
    """
    Supprime un lead
    """
    db_lead = db.query(LeadModel).filter(LeadModel.id == lead_id).first()
    if not db_lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    db.delete(db_lead)
    db.commit()
    return None

@router.get("/export", status_code=status.HTTP_200_OK)
def export_leads(
    campagne_id: Optional[int] = Query(None),
    format: str = Query("csv", regex="^(csv|excel)$"),
    db: Session = Depends(deps.get_db)
):
    """
    Exporte les leads au format CSV ou Excel
    """
    # Construire la requête
    query = db.query(LeadModel)
    
    if campagne_id:
        query = query.filter(LeadModel.campagne_id == campagne_id)
    
    leads = query.all()
    
    # Ici, vous implémenteriez la logique d'export réelle
    # Pour l'instant, nous retournons juste un message de succès
    return {"message": f"{len(leads)} leads exportés au format {format}"} 