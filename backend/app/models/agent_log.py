from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.base_class import Base

class AgentLog(Base):
    __tablename__ = "agent_logs"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    operation = Column(String)
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    status = Column(String)
    execution_time = Column(Float)
    
    # Système de feedback intégré
    feedback_score = Column(Float, nullable=True)  # Note de 0 à 5
    feedback_text = Column(Text, nullable=True)  # Commentaires explicatifs
    feedback_source = Column(String, default="auto")  # "auto", "human", "agent"
    feedback_timestamp = Column(DateTime, nullable=True)
    feedback_validated = Column(Boolean, default=False)  # Validé par un humain?
    
    # Relations
    agent = relationship("Agent", back_populates="logs")
