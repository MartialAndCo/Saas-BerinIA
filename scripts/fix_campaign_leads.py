#!/usr/bin/env python3
"""
Script pour corriger l'erreur de validation dans les campagnes Berinia.
L'erreur se produit car le champ 'leads' contient des objets Lead au lieu d'entiers.
"""

import os
import sys
import logging
from datetime import datetime

# Ajouter le répertoire racine au chemin Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Configurer logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("berinia-campaign-fix")

try:
    # Importer les modules nécessaires
    from sqlalchemy import create_engine, text
    
    # Importer la configuration de la base de données depuis le module d'intégration Berinia
    from integrations.berinia.db_connector import (
        DB_URL, 
        BERINIA_AVAILABLE,
        test_berinia_connection
    )

    if not BERINIA_AVAILABLE:
        logger.error("❌ Module d'intégration Berinia non disponible. Correction impossible.")
        sys.exit(1)
        
except ImportError as e:
    logger.error(f"❌ Impossible d'importer les modules nécessaires: {str(e)}")
    sys.exit(1)

def fix_campaign_leads():
    """
    Corrige les campagnes en réparant la relation avec les leads.
    """
    print(f"\n{'='*40}")
    print(f"🔧 CORRECTION DES CAMPAGNES BERINIA")
    print(f"🕒 Date et heure: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*40}\n")
    
    # Tester la connexion à la base de données
    print("🔍 Test de la connexion à la base de données...")
    if not test_berinia_connection():
        print("❌ Échec de la connexion à la base de données. Abandon.")
        return False
        
    print("✅ Connexion à la base de données réussie.")
    
    try:
        # Créer une connexion à la base de données
        engine = create_engine(DB_URL)
        
        with engine.connect() as conn:
            # Commencer une transaction
            trans = conn.begin()
            try:
                # 1. Vérification de la structure de la table leads
                print("🔍 Vérification de la structure de la table leads...")
                columns = conn.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'leads'")).fetchall()
                leads_columns = {col[0]: col[1] for col in columns}
                
                print(f"✅ Structure de la table leads: {leads_columns}")
                
                # 2. Vérification de la structure de la table campaigns
                print("🔍 Vérification de la structure de la table campaigns...")
                columns = conn.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'campaigns'")).fetchall()
                campaigns_columns = {col[0]: col[1] for col in columns}
                
                print(f"✅ Structure de la table campaigns: {campaigns_columns}")
                
                # 3. Correction: s'assurer que les leads référencent correctement les campagnes
                print("🔧 Correction des références entre leads et campaigns...")
                
                # Récupérer toutes les campagnes
                campaigns = conn.execute(text("SELECT id, nom FROM campaigns")).fetchall()
                print(f"📋 {len(campaigns)} campagnes trouvées.")
                
                # Pour chaque campagne, vérifier et corriger les leads associés
                for campaign in campaigns:
                    campaign_id = campaign[0]
                    campaign_name = campaign[1]
                    
                    # Compter les leads associés à cette campagne
                    lead_count = conn.execute(
                        text("SELECT COUNT(*) FROM leads WHERE campagne_id = :campaign_id"),
                        {"campaign_id": campaign_id}
                    ).scalar()
                    
                    print(f"📊 Campagne {campaign_name} (ID: {campaign_id}): {lead_count} leads associés")
                    
                    # Correction des relations (si nécessaire)
                    if 'leads' in campaigns_columns and campaigns_columns['leads'] != 'integer':
                        # Si la colonne leads existe et n'est pas de type integer
                        print(f"🔧 Correction de la structure de la colonne 'leads' dans la table campaigns...")
                        
                        # Solution: Renommer la colonne problématique et créer une nouvelle colonne correcte
                        try:
                            # Renommer la colonne problématique
                            conn.execute(text("ALTER TABLE campaigns RENAME COLUMN leads TO leads_old"))
                            
                            # Créer une nouvelle colonne de type integer
                            conn.execute(text("ALTER TABLE campaigns ADD COLUMN leads integer"))
                            
                            # Mettre à jour la nouvelle colonne avec le nombre de leads
                            conn.execute(text("""
                                UPDATE campaigns c
                                SET leads = (SELECT COUNT(*) FROM leads l WHERE l.campagne_id = c.id)
                            """))
                            
                            print("✅ Colonne 'leads' corrigée avec succès.")
                        except Exception as e:
                            print(f"❌ Erreur lors de la correction de la colonne 'leads': {str(e)}")
                    else:
                        # Si la colonne leads n'existe pas, la créer
                        if 'leads' not in campaigns_columns:
                            print(f"🔧 Création de la colonne 'leads' dans la table campaigns...")
                            conn.execute(text("ALTER TABLE campaigns ADD COLUMN leads integer"))
                            
                            # Mettre à jour la nouvelle colonne avec le nombre de leads
                            conn.execute(text("""
                                UPDATE campaigns c
                                SET leads = (SELECT COUNT(*) FROM leads l WHERE l.campagne_id = c.id)
                            """))
                            
                            print("✅ Colonne 'leads' créée avec succès.")
                        else:
                            # Mise à jour du compteur de leads (pour s'assurer qu'il est correct)
                            conn.execute(text("""
                                UPDATE campaigns c
                                SET leads = (SELECT COUNT(*) FROM leads l WHERE l.campagne_id = c.id)
                            """))
                            
                            print("✅ Compteur de leads mis à jour.")
                
                # Valider la transaction
                trans.commit()
                print("\n✅ Correction des campagnes terminée avec succès.")
                return True
                
            except Exception as e:
                # Annuler la transaction en cas d'erreur
                trans.rollback()
                print(f"❌ Erreur lors de la correction des campagnes: {str(e)}")
                return False
                
    except Exception as e:
        print(f"❌ Erreur lors de la connexion à la base de données: {str(e)}")
        return False

if __name__ == "__main__":
    success = fix_campaign_leads()
    
    if success:
        print("\n🚀 Pour redémarrer le système avec les campagnes corrigées, exécutez:")
        print("python3 start_brain_agent.py")
        sys.exit(0)
    else:
        print("\n❌ La correction a échoué.")
        sys.exit(1)
