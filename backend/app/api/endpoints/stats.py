from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
import sqlalchemy as sa
from sqlalchemy import func, text
from typing import Optional
from app.api import deps
from app.models.niche import Niche
from app.models.campaign import Campaign
from app.models.lead import Lead

router = APIRouter(tags=["Stats"])

@router.get("/overview")
def get_stats_overview(
    period: Optional[str] = Query("30d"),
    db: Session = Depends(deps.get_db)
):
    return {
        "leadsCollected": {
            "value": db.query(Lead).count(),
            "change": 12.5,
            "trend": "up"
        },
        "conversionRate": {
            "value": 8.2,
            "change": 2.1,
            "trend": "up"
        },
        "openRate": {
            "value": 24.5,
            "change": 4.3,
            "trend": "up"
        },
        "costPerLead": {
            "value": 2.35,
            "change": -0.45,
            "trend": "down"
        },
        "period": period
    }

@router.get("/conversion")
def get_conversion_chart(period: str = Query("30d")):
    return [
        {"date": "2024-04-01", "value": 5.2},
        {"date": "2024-04-02", "value": 5.8},
        {"date": "2024-04-03", "value": 6.1},
        {"date": "2024-04-04", "value": 7.3},
        {"date": "2024-04-05", "value": 8.2}
    ]

@router.get("/leads")
def leads_stats(period: Optional[str] = Query("30d"), db: Session = Depends(deps.get_db)):
    return [
        {"date": "2024-04-01", "value": 12},
        {"date": "2024-04-02", "value": 18},
        {"date": "2024-04-03", "value": 15},
        {"date": "2024-04-04", "value": 22},
        {"date": "2024-04-05", "value": 28}
    ]

@router.get("/campaigns")
def campaigns_stats(period: Optional[str] = Query("30d"), db: Session = Depends(deps.get_db)):
    return [
        {"name": "Agences immobilières Paris", "value": 78},
        {"name": "Avocats d'affaires Lyon", "value": 45},
        {"name": "Architectes Bordeaux", "value": 92},
        {"name": "Consultants RH Lille", "value": 24},
        {"name": "Cliniques vétérinaires", "value": 62}
    ]

@router.get("/niches")
def get_niche_stats(period: str = "30d", db: Session = Depends(deps.get_db)):
    days = int(period.replace("d", ""))

    subquery = (
        db.query(
            Campaign.niche_id.label("niche_id"),
            func.date_trunc("day", Lead.date_creation).label("day"),
            func.count(Lead.id).label("leads_count"),
            func.avg(func.nullif(Lead.statut != 'converti', True).cast(sa.Integer)).label("conversion_rate")
        )
        .join(Lead, Campaign.id == Lead.campagne_id)
        .filter(Lead.date_creation >= func.now() - func.cast(f"{days} days", sa.Interval))
        .group_by("niche_id", "day")
        .subquery()
    )

    rows = (
        db.query(
            Niche.nom.label("niche"),
            func.array_agg(
                subquery.c.leads_count.op("ORDER BY")(text("day"))
            ).label("trend"),
            func.avg(subquery.c.conversion_rate).label("conversion")
        )
        .join(subquery, subquery.c.niche_id == Niche.id)
        .group_by(Niche.nom)
        .all()
    )

    return [{"niche": row.niche, "trend": row.trend, "conversion": float(row.conversion)} for row in rows]
