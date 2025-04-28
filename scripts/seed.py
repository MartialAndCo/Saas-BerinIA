#!/usr/bin/env python3
"""
Script de seed pour remplir la base de données avec des données initiales.
Crée 3 niches, 3 campagnes (une par niche) et 3 leads (un par campagne).
"""

import sys
import os
from datetime import datetime
from pathlib import Path

# Ajouter le répertoire backend au path pour pouvoir importer les modules de l'application
current_dir = Path(__file__).parent
backend_dir = current_dir.parent / "backend"
sys.path.insert(0, str(backend_dir))

# Maintenant nous pouvons importer depuis le module app dans backend
from app.database.session import SessionLocal
from app.models.niche import Niche
from app.models.campaign import Campaign
from app.models.lead import Lead

print("Python path:", sys.path)
print("Current directory:", os.getcwd())

def seed_database():
    """Remplit la base de données avec des données initiales"""
    db = SessionLocal()
    
    try:
        print("🌱 Début du seeding de la base de données...")
        
        # Vérifier si des données existent déjà
        existing_niches = db.query(Niche).count()
        if existing_niches > 0:
            print("⚠️  Des données existent déjà dans la base. Nettoyage...")
            # Supprimer les données existantes (dans l'ordre pour respecter les contraintes de clé étrangère)
            db.query(Lead).delete()
            db.query(Campaign).delete()
            db.query(Niche).delete()
            db.commit()
        
        # Créer les niches
        niches = [
            Niche(
                nom="Marketing local",
                description="Agences de marketing digital spécialisées dans les PME locales",
                statut="Rentable",  # Ajusté selon l'enum dans le modèle
                taux_conversion=4.2,
                cout_par_lead=45.50,
                recommandation="Continuer",  # Ajusté selon l'enum dans le modèle
                date_creation=datetime.now()
            ),
            Niche(
                nom="Esthétique",
                description="Salons d'esthétique et instituts de beauté",
                statut="En test",  # Ajusté selon l'enum dans le modèle
                taux_conversion=3.8,
                cout_par_lead=38.75,
                recommandation="Développer",  # Ajusté selon l'enum dans le modèle
                date_creation=datetime.now()
            ),
            Niche(
                nom="Immobilier",
                description="Agents immobiliers indépendants",
                statut="En test",  # Ajusté selon l'enum dans le modèle
                taux_conversion=2.1,
                cout_par_lead=65.20,
                recommandation="Optimiser",  # Ajusté selon l'enum dans le modèle
                date_creation=datetime.now()
            )
        ]
        
        # Ajouter les niches à la base de données
        for niche in niches:
            db.add(niche)
        
        # Commit pour obtenir les IDs des niches
        db.commit()
        
        print(f"✅ {len(niches)} niches créées")
        
        # Créer les campagnes
        campaigns = [
            Campaign(
                nom="Campagne Google Ads - Marketing Local",  # Changé de name à nom selon le modèle
                description="Campagne de recherche Google pour agences marketing",
                statut="active",  # Changé de status à statut selon le modèle
                date_creation=datetime.now(),  # Changé de date à date_creation selon le modèle
                niche_id=niches[0].id
            ),
            Campaign(
                nom="Campagne Facebook - Esthétique",  # Changé de name à nom selon le modèle
                description="Campagne Facebook ciblant les propriétaires de salons d'esthétique",
                statut="active",  # Changé de status à statut selon le modèle
                date_creation=datetime.now(),  # Changé de date à date_creation selon le modèle
                niche_id=niches[1].id
            ),
            Campaign(
                nom="Campagne LinkedIn - Immobilier",  # Changé de name à nom selon le modèle
                description="Campagne LinkedIn pour agents immobiliers",
                statut="paused",  # Changé de status à statut selon le modèle
                date_creation=datetime.now(),  # Changé de date à date_creation selon le modèle
                niche_id=niches[2].id
            )
        ]
        
        # Ajouter les campagnes à la base de données
        for campaign in campaigns:
            db.add(campaign)
        
        # Commit pour obtenir les IDs des campagnes
        db.commit()
        
        print(f"✅ {len(campaigns)} campagnes créées")
        
        # Créer les leads
        leads = [
            Lead(
                nom="Sophie Martin",  # Changé de name à nom selon le modèle
                email="sophie.martin@agencelocale.fr",
                telephone="06 12 34 56 78",  # Changé de phone à telephone selon le modèle
                statut="qualified",  # Changé de status à statut selon le modèle
                date_creation=datetime.now(),  # Changé de date à date_creation selon le modèle
                campagne_id=campaigns[0].id  # Changé de campaign_id à campagne_id selon le modèle
            ),
            Lead(
                nom="Julie Dubois",  # Changé de name à nom selon le modèle
                email="julie@beaute-zen.fr",
                telephone="07 23 45 67 89",  # Changé de phone à telephone selon le modèle
                statut="contacted",  # Changé de status à statut selon le modèle
                date_creation=datetime.now(),  # Changé de date à date_creation selon le modèle
                campagne_id=campaigns[1].id  # Changé de campaign_id à campagne_id selon le modèle
            ),
            Lead(
                nom="Thomas Leroy",  # Changé de name à nom selon le modèle
                email="t.leroy@immo-conseil.fr",
                telephone="06 98 76 54 32",  # Changé de phone à telephone selon le modèle
                statut="new",  # Changé de status à statut selon le modèle
                date_creation=datetime.now(),  # Changé de date à date_creation selon le modèle
                campagne_id=campaigns[2].id  # Changé de campaign_id à campagne_id selon le modèle
            )
        ]
        
        # Ajouter les leads à la base de données
        for lead in leads:
            db.add(lead)
        
        # Commit final
        db.commit()
        
        print(f"✅ {len(leads)} leads créés")
        print("✅ Seeding terminé avec succès!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erreur lors du seeding: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database() 