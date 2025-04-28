#!/usr/bin/env python3
"""
Script pour créer une campagne de test dans la base de données Berinia.
Cette campagne pourra ensuite être utilisée pour y associer des leads.
"""

import os
import sys
import json
from datetime import datetime

# Ajouter le chemin du backend Berinia au PYTHONPATH
BERINIA_BACKEND_PATH = "/root/berinia/backend"
if BERINIA_BACKEND_PATH not in sys.path:
    sys.path.append(BERINIA_BACKEND_PATH)

try:
    from sqlalchemy import create_engine, text
    from app.database.session import SessionLocal
    from app.models.campaign import Campaign
    from app.models.niche import Niche
    
    # Importer les modules supplémentaires nécessaires
    import sqlalchemy
    print(f"SQLAlchemy version: {sqlalchemy.__version__}")
    print("✅ Modules importés avec succès")
    
except ImportError as e:
    print(f"❌ Erreur lors de l'importation des modules: {str(e)}")
    sys.exit(1)

def create_test_campaign():
    """
    Crée une campagne de test dans la base de données Berinia
    """
    try:
        # Établir une connexion à la base de données
        db = SessionLocal()
        
        # Vérifier si une niche existe (ID=1)
        niche = db.query(Niche).filter(Niche.id == 1).first()
        if not niche:
            print("❌ Aucune niche trouvée avec ID=1, création impossible")
            db.close()
            return False
            
        print(f"✅ Niche trouvée: {niche.nom} (ID={niche.id})")
        
        # Vérifier si une campagne de test existe déjà
        existing_campaign = db.query(Campaign).filter(Campaign.nom.like("Test%")).first()
        if existing_campaign:
            print(f"ℹ️ Une campagne de test existe déjà: {existing_campaign.nom} (ID={existing_campaign.id})")
            db.close()
            return True
        
        # Créer une nouvelle campagne
        new_campaign = Campaign(
            nom=f"Test Campaign {datetime.now().strftime('%Y%m%d%H%M')}",
            description="Campagne créée pour les tests d'intégration",
            statut="active",
            target_leads=100,
            agent="TestAgent",
            niche_id=niche.id
        )
        
        # Ajouter la campagne à la base de données
        db.add(new_campaign)
        db.commit()
        db.refresh(new_campaign)
        
        print(f"✅ Campagne créée avec succès: {new_campaign.nom} (ID={new_campaign.id})")
        
        # Récupérer toutes les campagnes pour vérification
        all_campaigns = db.query(Campaign).all()
        print("\nListe des campagnes:")
        for campaign in all_campaigns:
            print(f"  - ID {campaign.id}: {campaign.nom} (Niche ID: {campaign.niche_id})")
        
        db.close()
        return new_campaign.id
        
    except Exception as e:
        print(f"❌ Erreur lors de la création de la campagne: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== Création d'une campagne de test dans Berinia ===")
    print(f"📅 Date: {datetime.now().isoformat()}")
    
    campaign_id = create_test_campaign()
    
    print("\n=== Récapitulatif ===")
    if campaign_id:
        print(f"✅ Campagne créée ou existante (ID: {campaign_id})")
        print(f"   Utilisez cet ID pour les tests d'insertion de leads")
        sys.exit(0)
    else:
        print("❌ La création de la campagne a échoué")
        sys.exit(1)
