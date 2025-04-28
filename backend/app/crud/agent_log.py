from typing import Dict, List, Optional, Union, Any
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.agent_log import AgentLog
from app.schemas.agent_log import AgentLogCreate, AgentLogUpdate, AgentLogFeedback

def get_logs(db: Session, skip: int = 0, limit: int = 100, agent_id: Optional[int] = None):
    query = db.query(AgentLog)
    if agent_id:
        query = query.filter(AgentLog.agent_id == agent_id)
    return query.order_by(AgentLog.timestamp.desc()).offset(skip).limit(limit).all()

def get(db: Session, id: int):
    return db.query(AgentLog).filter(AgentLog.id == id).first()

def create(db: Session, obj_in: AgentLogCreate):
    obj_in_data = obj_in.dict()
    db_obj = AgentLog(**obj_in_data)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update(db: Session, db_obj: AgentLog, obj_in: Union[AgentLogUpdate, Dict[str, Any]]):
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.dict(exclude_unset=True)
    
    for field in update_data:
        if field in update_data:
            setattr(db_obj, field, update_data[field])
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def remove(db: Session, id: int):
    obj = db.query(AgentLog).get(id)
    db.delete(obj)
    db.commit()
    return obj

def add_feedback(db: Session, log_id: int, feedback: AgentLogFeedback):
    log = get(db, id=log_id)
    if not log:
        return None
    
    update_data = {
        "feedback_score": feedback.score,
        "feedback_text": feedback.text,
        "feedback_source": feedback.source,
        "feedback_timestamp": datetime.utcnow(),
        "feedback_validated": feedback.validated
    }
    
    updated_log = update(db, log, update_data)
    
    # Mettre à jour le score moyen de l'agent
    if updated_log:
        from app.crud import agent as agent_crud
        
        # Récupérer tous les logs avec feedback pour cet agent
        agent_logs = db.query(AgentLog).filter(
            AgentLog.agent_id == updated_log.agent_id,
            AgentLog.feedback_score.isnot(None)
        ).all()
        
        if agent_logs:
            avg_score = sum(log.feedback_score for log in agent_logs) / len(agent_logs)
            agent_crud.update_feedback_score(db, updated_log.agent_id, avg_score)
    
    return updated_log

def get_feedback_stats(db: Session, agent_id: int):
    # Statistiques globales de feedback pour un agent
    logs = db.query(AgentLog).filter(
        AgentLog.agent_id == agent_id,
        AgentLog.feedback_score.isnot(None)
    ).all()
    
    if not logs:
        return {
            "total_feedbacks": 0,
            "average_score": 0,
            "distribution": {
                "excellent": 0,
                "good": 0,
                "average": 0,
                "poor": 0,
                "bad": 0
            }
        }
    
    avg_score = sum(log.feedback_score for log in logs) / len(logs)
    
    # Distribution des scores
    excellent = len([log for log in logs if log.feedback_score >= 4.5])
    good = len([log for log in logs if 3.5 <= log.feedback_score < 4.5])
    average = len([log for log in logs if 2.5 <= log.feedback_score < 3.5])
    poor = len([log for log in logs if 1.5 <= log.feedback_score < 2.5])
    bad = len([log for log in logs if log.feedback_score < 1.5])
    
    return {
        "total_feedbacks": len(logs),
        "average_score": avg_score,
        "distribution": {
            "excellent": excellent,
            "good": good,
            "average": average,
            "poor": poor,
            "bad": bad
        }
    }
