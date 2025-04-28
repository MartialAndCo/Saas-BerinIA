#!/usr/bin/env python3
"""
Script simple pour vider la base de données Berinia.
"""

import os
import sys
import logging
from datetime import datetime

# Ajouter le répertoire racine au chemin Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Importer les modules de base de données
try:
    from sqlalchemy import create_engine, text
    from integrations.berinia.db_connector import DB_URL, test_berinia_connection
except ImportError as e:
    print(f"❌ Erreur d'importation: {str(e)}")
    sys.exit(1)

def vider_base_berinia():
    """Vide simplement tous les leads de la base de données."""
    print("\n=== VIDAGE DE LA BASE DE DONNÉES BERINIA ===")
    print(f"📅 Date: {datetime.now().isoformat()}")
    
    # Vérifier la connexion
    print("🔍 Test de connexion à la base de données...")
    if not test_berinia_connection():
        print("❌ Échec de la connexion à la base de données")
        return False
    
    print("✅ Connexion réussie")
    
    # Créer une connexion
    engine = create_engine(DB_URL)
    
    try:
        with engine.connect() as conn:
            # Vider la table des leads
            print("🧹 Suppression de tous les leads...")
            result = conn.execute(text("DELETE FROM leads"))
            conn.commit()
            print(f"✅ {result.rowcount} leads supprimés avec succès")
            return True
    except Exception as e:
        print(f"❌ Erreur lors du vidage de la base: {str(e)}")
        return False

if __name__ == "__main__":
    success = vider_base_berinia()
    
    if success:
        print("\n✅ Base de données vidée avec succès")
        print("🚀 Pour redémarrer le système avec une base propre, lancez:")
        print("python3 start_brain_agent.py")
    else:
        print("\n❌ Échec du vidage de la base de données")
