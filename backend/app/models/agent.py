from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.base_class import Base

class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, index=True)
    type = Column(String)
    statut = Column(String, default="inactive")
    derniere_execution = Column(DateTime, nullable=True)
    leads_generes = Column(Integer, default=0)
    campagnes_actives = Column(Integer, default=0)
    date_creation = Column(DateTime, default=datetime.utcnow)
    
    # Colonnes additionnelles pour l'infrastructure avancée d'agents
    configuration = Column(JSON, nullable=True)  # Stockage des configs spécifiques
    prompt_template = Column(Text, nullable=True)  # Template de prompt
    metrics = Column(JSON, nullable=True)  # Métriques de performance
    dependencies = Column(JSON, nullable=True)  # Dépendances entre agents
    log_level = Column(String, default="INFO")
    feedback_score = Column(Float, default=0.0)  # Score moyen de feedback
    last_feedback_date = Column(DateTime, nullable=True)  # Date du dernier feedback
    
    # Relations
    logs = relationship("AgentLog", back_populates="agent", cascade="all, delete-orphan")
