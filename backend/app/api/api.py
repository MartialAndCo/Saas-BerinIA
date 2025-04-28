from fastapi import APIRouter
from app.api.endpoints import stats, dashboard, logs, niches, campaigns, leads, agents, messages

api_router = APIRouter()

# Les endpoints statiques et non dynamiques d'abord
api_router.include_router(stats.router, prefix="/stats", tags=["stats"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(logs.router, prefix="/logs", tags=["logs"])

# Les endpoints principaux
api_router.include_router(niches.router, prefix="/niches", tags=["niches"])
api_router.include_router(campaigns.router, prefix="/campaigns", tags=["campaigns"])
api_router.include_router(leads.router, prefix="/leads", tags=["leads"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(messages.router, prefix="/messages", tags=["messages"])
