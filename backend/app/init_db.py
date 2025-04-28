#!/usr/bin/env python3
"""
Script d'initialisation de la base de données.
Crée toutes les tables définies dans les modèles SQLAlchemy.
"""

import os
import sys
from pathlib import Path

# Ajouter le répertoire parent au sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Importer les modules nécessaires
from app.database.base import Base
from app.database.session import engine
from app.models.log import Log
from app.models.user import User
from app.models.niche import Niche
from app.models.lead import Lead
from app.models.campaign import Campaign
from app.models.agent import Agent

def init_db():
    """Initialiser la base de données en créant toutes les tables."""
    print("Création des tables dans la base de données...")
    Base.metadata.create_all(bind=engine)
    print("Base de données initialisée avec succès!")

if __name__ == "__main__":
    init_db() 