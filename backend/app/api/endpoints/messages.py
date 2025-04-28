from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.api import deps
from app.models.message import Message as MessageModel
from app.schemas.message import Message, MessageCreate, MessageUpdate, MessageResponse, PaginatedMessageResponse

router = APIRouter(tags=["Messages"])

@router.get("/", response_model=PaginatedMessageResponse)
def get_messages(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    status: Optional[str] = Query(None),
    campaign_id: Optional[int] = Query(None),
    lead_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(deps.get_db)
):
    """
    Récupère la liste des messages avec filtres optionnels
    """
    # Construire la requête de base
    query = db.query(MessageModel)
    
    # Appliquer les filtres
    if status:
        query = query.filter(MessageModel.status == status)
    
    if campaign_id:
        query = query.filter(MessageModel.campaign_id == campaign_id)
    
    if lead_id:
        query = query.filter(MessageModel.lead_id == lead_id)
    
    if search:
        query = query.filter(
            (MessageModel.subject.ilike(f"%{search}%")) | 
            (MessageModel.content.ilike(f"%{search}%"))
        )
    
    # Compter le total
    total = query.count()
    
    # Exécuter la requête avec pagination
    messages = query.offset(skip).limit(limit).all()
    
    # Calculer le nombre de pages
    total_pages = (total + limit - 1) // limit
    
    return {
        "items": messages,
        "total": total,
        "page": skip // limit + 1,
        "limit": limit,
        "totalPages": total_pages
    }

@router.post("/", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def create_message(message: MessageCreate, db: Session = Depends(deps.get_db)):
    """
    Crée un nouveau message
    """
    db_message = MessageModel(
        lead_id=message.lead_id,
        lead_name=message.lead_name,
        lead_email=message.lead_email,
        subject=message.subject,
        content=message.content,
        status="sent",
        campaign_id=message.campaign_id,
        campaign_name=message.campaign_name,
        sent_date=datetime.utcnow()
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

@router.get("/{message_id}", response_model=MessageResponse)
def get_message(message_id: int, db: Session = Depends(deps.get_db)):
    """
    Récupère un message spécifique par son ID
    """
    message = db.query(MessageModel).filter(MessageModel.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return message

@router.post("/{message_id}/resend", response_model=MessageResponse)
def resend_message(message_id: int, db: Session = Depends(deps.get_db)):
    """
    Renvoie un message existant
    """
    message = db.query(MessageModel).filter(MessageModel.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    # Créer une copie du message avec une nouvelle date d'envoi
    new_message = MessageModel(
        lead_id=message.lead_id,
        lead_name=message.lead_name,
        lead_email=message.lead_email,
        subject=f"RE: {message.subject}",
        content=message.content,
        status="sent",
        campaign_id=message.campaign_id,
        campaign_name=message.campaign_name,
        sent_date=datetime.utcnow()
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message

@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_message(message_id: int, db: Session = Depends(deps.get_db)):
    """
    Supprime un message
    """
    message = db.query(MessageModel).filter(MessageModel.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    db.delete(message)
    db.commit()
    return None

@router.get("/stats", response_model=dict)
def get_message_stats(campaign_id: Optional[int] = Query(None), db: Session = Depends(deps.get_db)):
    """
    Récupère les statistiques des messages
    """
    query = db.query(MessageModel)
    
    if campaign_id:
        query = query.filter(MessageModel.campaign_id == campaign_id)
    
    total = query.count()
    sent = query.filter(MessageModel.status == "sent").count()
    delivered = query.filter(MessageModel.status == "delivered").count()
    opened = query.filter(MessageModel.status == "opened").count()
    clicked = query.filter(MessageModel.status == "clicked").count()
    replied = query.filter(MessageModel.status == "replied").count()
    bounced = query.filter(MessageModel.status == "bounced").count()
    failed = query.filter(MessageModel.status == "failed").count()
    
    return {
        "total": total,
        "sent": sent,
        "delivered": delivered,
        "opened": opened,
        "clicked": clicked,
        "replied": replied,
        "bounced": bounced,
        "failed": failed,
        "open_rate": (opened / delivered * 100) if delivered > 0 else 0,
        "click_rate": (clicked / opened * 100) if opened > 0 else 0,
        "reply_rate": (replied / delivered * 100) if delivered > 0 else 0,
        "bounce_rate": (bounced / total * 100) if total > 0 else 0
    } 