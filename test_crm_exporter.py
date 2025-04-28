#!/usr/bin/env python3
"""
Script de test pour le CRMExporterAgent
"""

import json
import logging
from agents.exporter.crm_exporter_agent import CRMExporterAgent
from integrations.berinia.db_connector import test_berinia_connection

# Configuration du logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("test_crm_exporter")

def main():
    """Test du CRMExporterAgent avec des leads factices"""
    logger.info("========== DÉBUT DU TEST CRMExporterAgent ==========")
    
    # Tester la connexion Berinia
    logger.info("Test de la connexion Berinia...")
    berinia_available = test_berinia_connection()
    logger.info(f"Connexion Berinia disponible: {berinia_available}")
    
    # Préparer des leads factices pour le test
    test_leads = [
        {
            "id": "test_lead_1",
            "company_name": "Entreprise Test 1",
            "email": "contact@test1.com",
            "phone": "+33123456789",
            "classification": {
                "qualite_lead": "WARM",
                "score": 0.75,
                "priorite": "élevée"
            }
        },
        {
            "id": "test_lead_2",
            "company_name": "Entreprise Test 2",
            "email": "",  # Email vide pour tester la robustesse
            "phone": "+33987654321",
            "classification": {
                "qualite_lead": "COLD",
                "score": 0.35,
                "priorite": "basse"
            }
        },
        {
            "id": "test_lead_3",
            "company_name": "Entreprise Test 3",
            "email": "info@test3.fr",
            "phone": "+33555555555",
            "classification": {
                "qualite_lead": "HOT",
                "score": 0.9,
                "priorite": "très élevée"
            }
        }
    ]
    
    # Préparer les données d'entrée
    input_data = {
        "classified_leads": test_leads,
        "pending_leads_count": 5,
        "daily_limit": 20,
        "exported_today": 10,
        "campaign_id": 123
    }
    
    # Créer l'agent d'exportation
    exporter = CRMExporterAgent()
    
    # Exécuter l'agent
    logger.info("Exécution de l'agent d'exportation...")
    result = exporter.run(input_data)
    
    # Afficher le résultat
    logger.info("Résultat de l'exportation:")
    logger.info(json.dumps(result, indent=2, ensure_ascii=False))
    
    # Analyser le résultat
    if "export_status" in result:
        if result["export_status"] == "success":
            logger.info(f"✅ Exportation réussie: {result.get('leads_count', 0)} leads exportés")
        elif result["export_status"] == "simulated":
            logger.info(f"🔄 Exportation simulée: {result.get('leads_count', 0)} leads seraient exportés")
        else:
            logger.info(f"❌ Exportation échouée: {result.get('error', 'Raison inconnue')}")
    else:
        logger.warning("Format de résultat inattendu, status d'exportation non trouvé")
    
    logger.info("========== FIN DU TEST CRMExporterAgent ==========")

if __name__ == "__main__":
    main()
