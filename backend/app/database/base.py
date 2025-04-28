# Import base class for SQLAlchemy models
from app.database.base_class import Base

# Import all models so that they are registered with SQLAlchemy
from app.models.user import User
from app.models.niche import Niche
from app.models.lead import Lead
from app.models.campaign import Campaign
from app.models.agent import Agent
# Importez d'autres modèles si nécessaire
# from app.models.log import Log

# All models should be imported here 