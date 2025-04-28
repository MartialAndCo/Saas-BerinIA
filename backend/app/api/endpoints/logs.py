from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
import logging
from app.api import deps
from app.models.log import Log
from app.schemas.log import LogResponse

router = APIRouter(tags=["Logs"])

logger = logging.getLogger(__name__)

@router.get("/recent", response_model=List[LogResponse])
def get_recent_logs(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(deps.get_db)
):
    try:
        logs = db.query(Log).order_by(Log.timestamp.desc()).limit(limit).all()
        return logs
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des logs: {str(e)}")
        # Si la table n'existe pas, créez-la
        if "relation" in str(e) and "does not exist" in str(e):
            from app.database.base import Base
            from app.database.session import engine
            Base.metadata.create_all(bind=engine)
            logger.info("Table logs créée. Réessayez la requête.")
        raise HTTPException(
            status_code=500, 
            detail="Erreur lors de la récupération des logs. Vérifiez les logs serveur pour plus de détails."
        ) 