from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.base_class import Base

class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, index=True)
    email = Column(String)
    telephone = Column(String, nullable=True)
    entreprise = Column(String, nullable=True)
    date_creation = Column(DateTime, default=datetime.utcnow)
    statut = Column(String, default="new")

    campagne_id = Column(Integer, ForeignKey("campaigns.id"))
    campaign = relationship("Campaign", back_populates="leads")
    messages = relationship("Message", back_populates="lead")
