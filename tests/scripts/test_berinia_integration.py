#!/usr/bin/env python3
"""
Script de test pour vérifier l'intégration avec la base de données Berinia.
Ce script teste l'exportation des leads dans la base de données Berinia.
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

# Données de test
TEST_LEADS = [
    {
        "id": "test-lead-1",
        "company_name": "Entreprise Test 1",
        "contact_name": "Jean Dupont",
        "email": "jean.dupont@example.com",
        "phone": "+33123456789",
        "website": "https://example.com",
        "campaign_id": 1
    },
    {
        "id": "test-lead-2",
        "company_name": "Entreprise Test 2",
        "contact_name": "Marie Martin",
        "email": "marie.martin@example.com",
        "phone": "+33987654321",
        "website": "https://example2.com",
        "campaign_id": 1
    }
]

def test_berinia_integration():
    """
    Teste l'intégration avec la base de données Berinia
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
    
    # Test d'exportation des leads
    print(f"🔍 Test d'exportation de {len(TEST_LEADS)} leads...")
    export_result = export_leads_to_berinia(TEST_LEADS)
    
    if not export_result.get("success", False):
        print(f"❌ Échec de l'exportation: {export_result.get('error', 'Erreur inconnue')}")
        return False
    
    print(f"✅ Exportation réussie: {export_result.get('leads_count', 0)} leads exportés")
    print(f"📊 Résultats: {json.dumps(export_result, indent=2)}")
    
    return True

if __name__ == "__main__":
    print("=== Test d'intégration avec Berinia ===")
    print(f"📅 Date: {datetime.now().isoformat()}")
    
    success = test_berinia_integration()
    
    print("\n=== Résultat du test ===")
    if success:
        print("✅ Test réussi - L'intégration fonctionne correctement")
        sys.exit(0)
    else:
        print("❌ Test échoué - L'intégration ne fonctionne pas correctement")
        sys.exit(1)
