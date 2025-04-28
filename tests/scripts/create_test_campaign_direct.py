#!/usr/bin/env python3
"""
Script pour créer une campagne de test directement avec SQL.
Contourne les potentiels problèmes avec les modèles ORM.
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
    
    # Tester la connexion à la base de données
    engine = create_engine(os.environ.get("DATABASE_URL", "postgresql://berinia_user:Bhcmi6pm_@localhost/berinia"))
    connection = engine.connect()
    print("✅ Connexion à la base de données réussie")
    
except ImportError as e:
    print(f"❌ Erreur lors de l'importation des modules: {str(e)}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Erreur de connexion: {str(e)}")
    sys.exit(1)

def create_test_campaign():
    """
    Crée une campagne de test directement avec SQL
    """
    try:
        # Vérifier si une campagne de test existe déjà
        result = connection.execute(text("SELECT id, nom FROM campaigns WHERE nom LIKE 'Test%'"))
        existing_campaigns = result.fetchall()
        
        if existing_campaigns:
            campaign_id = existing_campaigns[0][0]
            campaign_name = existing_campaigns[0][1]
            print(f"ℹ️ Une campagne de test existe déjà: {campaign_name} (ID={campaign_id})")
            return campaign_id
        
        # Vérifier qu'une niche existe
        result = connection.execute(text("SELECT id, nom FROM niches"))
        niches = result.fetchall()
        
        if not niches:
            print("❌ Aucune niche trouvée, création d'une niche par défaut")
            connection.execute(text("INSERT INTO niches (nom, description) VALUES ('Default', 'Default niche for testing')"))
            connection.commit()
            niche_id = 1
        else:
            niche_id = niches[0][0]
            print(f"✅ Niche trouvée: {niches[0][1]} (ID={niche_id})")
        
        # Créer une nouvelle campagne
        campaign_name = f"Test Campaign {datetime.now().strftime('%Y%m%d%H%M')}"
        result = connection.execute(
            text("INSERT INTO campaigns (nom, description, date_creation, statut, target_leads, agent, niche_id) "
                 "VALUES (:nom, :description, :date_creation, :statut, :target_leads, :agent, :niche_id) RETURNING id"),
            {
                "nom": campaign_name,
                "description": "Campagne créée pour les tests d'intégration",
                "date_creation": datetime.now(),
                "statut": "active",
                "target_leads": 100,
                "agent": "TestAgent",
                "niche_id": niche_id
            }
        )
        
        connection.commit()
        campaign_id = result.fetchone()[0]
        
        print(f"✅ Campagne créée avec succès: {campaign_name} (ID={campaign_id})")
        
        # Récupérer toutes les campagnes pour vérification
        result = connection.execute(text("SELECT id, nom, niche_id FROM campaigns"))
        all_campaigns = result.fetchall()
        
        print("\nListe des campagnes:")
        for campaign in all_campaigns:
            print(f"  - ID {campaign[0]}: {campaign[1]} (Niche ID: {campaign[2]})")
        
        return campaign_id
        
    except Exception as e:
        print(f"❌ Erreur lors de la création de la campagne: {str(e)}")
        connection.rollback()
        return False

if __name__ == "__main__":
    print("=== Création d'une campagne de test dans Berinia ===")
    print(f"📅 Date: {datetime.now().isoformat()}")
    
    try:
        campaign_id = create_test_campaign()
        
        print("\n=== Récapitulatif ===")
        if campaign_id:
            print(f"✅ Campagne créée ou existante (ID: {campaign_id})")
            print(f"   Utilisez cet ID pour les tests d'insertion de leads")
            connection.close()
            sys.exit(0)
        else:
            print("❌ La création de la campagne a échoué")
            connection.close()
            sys.exit(1)
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        sys.exit(1)
    finally:
        if 'connection' in locals():
            connection.close()
