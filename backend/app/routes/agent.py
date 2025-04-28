from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.schemas.agent import AgentCreate, Agent
from app.models.agent import Agent as AgentModel

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/api/agents", response_model=Agent)
def create_agent(agent: AgentCreate, db: Session = Depends(get_db)):
    db_agent = AgentModel(nom=agent.nom, statut=agent.statut)
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent

@router.get("/api/agents", response_model=list[Agent])
def get_agents(db: Session = Depends(get_db)):
    return db.query(AgentModel).all()
