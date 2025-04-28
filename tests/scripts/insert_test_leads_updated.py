#!/usr/bin/env python3
"""
Script pour insérer des leads de test dans la base de données Berinia.
Utilisé pour vérifier que l'intégration fonctionne correctement.
"""

import os
import sys
import json
from datetime import datetime

# Ajouter le répertoire racine au chemin Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

try:
    from integrations.berinia.db_connector import export_leads_to_berinia, test_berinia_connection
    INTEGRATION_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Erreur lors de l'importation du module d'intégration: {str(e)}")
    INTEGRATION_AVAILABLE = False

# Données de test - leads avec des données plus réalistes
TEST_LEADS = [
    {
        "id": "test-lead-1",
        "company_name": "Restaurant Le Gourmet",
        "contact_name": "Jean Dupont",
        "email": "contact@legourmet.fr",
        "phone": "+33123456789",
        "website": "https://legourmet.fr",
        "address": "15 rue de la Gastronomie, 75001 Paris",
        "status": "new",
        "business_type": "Restaurant",
        "score": 85,
        "campaign_id": 1  # Utiliser l'ID de la campagne créée
    },
    {
        "id": "test-lead-2",
        "company_name": "Boulangerie Miette",
        "contact_name": "Marie Martin",
        "email": "marie.martin@miette.fr",
        "phone": "+33987654321",
        "website": "https://boulangerie-miette.fr",
        "address": "27 avenue des Croissants, 75015 Paris",
        "status": "new",
        "business_type": "Boulangerie",
        "score": 78,
        "campaign_id": 1  # Utiliser l'ID de la campagne créée
    },
    {
        "id": "test-lead-3",
        "company_name": "Café Parisien",
        "contact_name": "Pierre Leroy",
        "email": "info@cafeparisien.fr",
        "phone": "+33645781245",
        "website": "https://cafe-parisien.fr",
        "address": "5 place de la République, 75011 Paris",
        "status": "new",
        "business_type": "Café",
        "score": 92,
        "campaign_id": 1  # Utiliser l'ID de la campagne créée
    }
]

def insert_test_leads():
    """
    Insère des leads de test dans la base de données Berinia
    """
    if not INTEGRATION_AVAILABLE:
        print("⚠️ Module d'intégration non disponible. Test impossible.")
        return False
    
    print("🔍 Test de connexion à la base de données Berinia...")
    connection_success = test_berinia_connection()
    
    if not connection_success:
        print("❌ Échec de la connexion à la base de données")
        return False
    
    print("✅ Connexion à la base de données réussie")
    
    # Insérer les leads de test
    print(f"🔄 Insertion de {len(TEST_LEADS)} leads de test...")
    export_result = export_leads_to_berinia(TEST_LEADS, campaign_id=1)  # Spécifier l'ID de campagne explicitement
    
    if not export_result.get("success", False):
        print(f"❌ Échec de l'insertion: {export_result.get('error', 'Erreur inconnue')}")
        return False
    
    print(f"✅ Insertion réussie: {export_result.get('leads_count', 0)} leads insérés")
    print(f"📊 Résultats détaillés: {json.dumps(export_result, indent=2)}")
    
    return True

if __name__ == "__main__":
    print("=== Insertion de leads de test dans Berinia ===")
    print(f"📅 Date: {datetime.now().isoformat()}")
    
    success = insert_test_leads()
    
    print("\n=== Récapitulatif ===")
    if success:
        print("✅ Tous les leads ont été insérés avec succès")
        sys.exit(0)
    else:
        print("❌ L'insertion des leads a échoué")
        sys.exit(1)
