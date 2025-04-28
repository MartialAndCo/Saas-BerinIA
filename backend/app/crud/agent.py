from typing import Dict, List, Optional, Union, Any
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.agent import Agent
from app.schemas.agent import AgentCreate, AgentUpdate

def get_agents(db: Session, skip: int = 0, limit: int = 100, status: Optional[str] = None):
    query = db.query(Agent)
    if status:
        query = query.filter(Agent.statut == status)
    return query.offset(skip).limit(limit).all()

def get(db: Session, id: int):
    return db.query(Agent).filter(Agent.id == id).first()

def create(db: Session, obj_in: AgentCreate):
    obj_in_data = obj_in.dict()
    db_obj = Agent(**obj_in_data)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update(db: Session, db_obj: Agent, obj_in: Union[AgentUpdate, Dict[str, Any]]):
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
    obj = db.query(Agent).get(id)
    db.delete(obj)
    db.commit()
    return obj

def get_agent_with_logs(db: Session, id: int):
    return db.query(Agent).filter(Agent.id == id).first()

def update_metrics(db: Session, agent_id: int, metrics: Dict[str, Any]):
    agent = get(db, id=agent_id)
    if agent:
        agent.metrics = metrics
        db.add(agent)
        db.commit()
        db.refresh(agent)
    return agent

def update_feedback_score(db: Session, agent_id: int, feedback_score: float):
    agent = get(db, id=agent_id)
    if agent:
        agent.feedback_score = feedback_score
        agent.last_feedback_date = datetime.utcnow()
        db.add(agent)
        db.commit()
        db.refresh(agent)
    return agent
