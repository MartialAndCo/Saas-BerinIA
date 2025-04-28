#!/usr/bin/env python3
"""
Script pour réinitialiser la base de données Berinia.
Ce script supprime tous les leads et réinitialise les séquences d'identifiants.
"""

import os
import sys
import logging
from datetime import datetime

# Ajouter le répertoire racine au chemin Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Configurer logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("berinia-reset")

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
        logger.error("❌ Module d'intégration Berinia non disponible. Réinitialisation impossible.")
        sys.exit(1)
        
except ImportError as e:
    logger.error(f"❌ Impossible d'importer les modules nécessaires: {str(e)}")
    sys.exit(1)

def reset_berinia_database(preserve_campaigns=True):
    """
    Réinitialise la base de données Berinia en supprimant les leads et en réinitialisant les séquences.
    
    Args:
        preserve_campaigns: Si True, conserve les campagnes existantes. Sinon, supprime également les campagnes.
    """
    print(f"\n{'='*40}")
    print(f"🧹 RÉINITIALISATION DE LA BASE DE DONNÉES BERINIA")
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
                # 1. Supprimer les leads
                print("🗑️ Suppression des leads de la base de données...")
                result = conn.execute(text("DELETE FROM leads"))
                print(f"✅ {result.rowcount} leads supprimés avec succès.")
                
                # 2. Réinitialiser la séquence d'ID des leads
                print("🔄 Réinitialisation de la séquence d'ID des leads...")
                conn.execute(text("ALTER SEQUENCE leads_id_seq RESTART WITH 1"))
                print("✅ Séquence d'ID des leads réinitialisée.")
                
                # 3. Facultatif: Supprimer les campagnes
                if not preserve_campaigns:
                    print("🗑️ Suppression des campagnes...")
                    result = conn.execute(text("DELETE FROM campaigns"))
                    print(f"✅ {result.rowcount} campagnes supprimées avec succès.")
                    
                    print("🔄 Réinitialisation de la séquence d'ID des campagnes...")
                    conn.execute(text("ALTER SEQUENCE campaigns_id_seq RESTART WITH 1"))
                    print("✅ Séquence d'ID des campagnes réinitialisée.")
                else:
                    print("ℹ️ Les campagnes existantes ont été conservées.")
                
                # Valider la transaction
                trans.commit()
                print("\n✅ Réinitialisation de la base de données Berinia réussie.")
                return True
                
            except Exception as e:
                # Annuler la transaction en cas d'erreur
                trans.rollback()
                print(f"❌ Erreur lors de la réinitialisation de la base de données: {str(e)}")
                return False
                
    except Exception as e:
        print(f"❌ Erreur lors de la connexion à la base de données: {str(e)}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Réinitialiser la base de données Berinia.')
    parser.add_argument('--with-campaigns', action='store_true', 
                        help='Supprimer également les campagnes (par défaut: conserver les campagnes)')
    args = parser.parse_args()
    
    success = reset_berinia_database(preserve_campaigns=not args.with_campaigns)
    
    if success:
        print("\n🚀 Pour redémarrer le système avec une base propre, exécutez:")
        print("sudo systemctl restart infra-ia-agents")
        sys.exit(0)
    else:
        print("\n❌ La réinitialisation a échoué.")
        sys.exit(1)
