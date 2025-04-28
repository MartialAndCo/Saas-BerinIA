from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.base_class import Base

class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, index=True)
    description = Column(Text, nullable=True)
    date_creation = Column(DateTime, default=datetime.utcnow)
    statut = Column(String, default="active")
    target_leads = Column(Integer, default=0)
    agent = Column(String, nullable=True)
    progress = Column(Integer, default=0)
    conversion = Column(Float, default=0.0)

    niche_id = Column(Integer, ForeignKey("niches.id"))
    niche = relationship("Niche", back_populates="campaigns")

    leads = relationship("Lead", back_populates="campaign")
    messages = relationship("Message", back_populates="campaign")
