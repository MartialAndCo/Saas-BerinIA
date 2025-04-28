from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.api import deps
from app.models.lead import Lead
from app.models.campaign import Campaign
from app.models.niche import Niche
from app.models.agent import Agent  # Si tu as un modèle Agent

router = APIRouter()

@router.get("/metrics")
def get_dashboard_metrics(db: Session = Depends(deps.get_db)):
    # Calcul des leads
    total_leads = db.query(func.count(Lead.id)).scalar() or 0
    leads_today = db.query(func.count(Lead.id)).filter(func.date(Lead.date_creation) == datetime.utcnow().date()).scalar() or 0

    # Calcul des campagnes
    total_campaigns = db.query(func.count(Campaign.id)).scalar() or 0
    active_campaigns = db.query(func.count(Campaign.id)).filter(Campaign.statut == "active").scalar() or 0
    pending_campaigns = total_campaigns - active_campaigns

    # Calcul des niches
    total_niches = db.query(func.count(Niche.id)).scalar() or 0
    profitable_niches = db.query(func.count(Niche.id)).filter(Niche.statut == "Rentable").scalar() or 0

    # Calcul des agents
    total_agents = db.query(func.count(Agent.id)).scalar() if db.query(Agent.id).first() else 0
    active_agents = db.query(func.count(Agent.id)).filter(Agent.statut == "active").scalar() if total_agents else 0
    error_agents = db.query(func.count(Agent.id)).filter(Agent.statut == "error").scalar() if total_agents else 0

    return {
        "leads": {
            "total": total_leads,
            "today": leads_today,
            "trend": "neutral",
            "trendValue": "0%"
        },
        "campaigns": {
            "active": active_campaigns,
            "pending": pending_campaigns,
            "trend": "neutral",
            "trendValue": "0"
        },
        "niches": {
            "explored": total_niches,
            "profitable": profitable_niches,
            "trend": "neutral",
            "trendValue": "0"
        },
        "agents": {
            "active": active_agents,
            "total": total_agents,
            "error": error_agents,
            "trend": "neutral"
        }
    }
