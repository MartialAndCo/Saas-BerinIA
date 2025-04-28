from sqlalchemy.orm import Session
from app.models.agent import Agent
from app.schemas.agent import AgentCreate

def create_agent(db: Session, agent: AgentCreate) -> Agent:
    db_agent = Agent(**agent.dict())
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent

def get_agents(db: Session):
    return db.query(Agent).all()
