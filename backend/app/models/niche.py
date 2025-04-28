from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.base_class import Base

class Niche(Base):
    __tablename__ = "niches"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, index=True)
    description = Column(Text, nullable=True)
    date_creation = Column(DateTime(timezone=True), server_default=func.now())

    statut = Column(String, default='En test')
    taux_conversion = Column(Float, default=0.0)
    cout_par_lead = Column(Float, default=0.0)
    recommandation = Column(String, default='Continuer')

    campaigns = relationship("Campaign", back_populates="niche")
