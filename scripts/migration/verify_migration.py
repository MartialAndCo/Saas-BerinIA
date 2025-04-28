#!/usr/bin/env python3
"""
Script de vérification de la migration du scraper Apify.
Confirme que le système utilise bien la nouvelle implémentation avec ApifyClient.
"""

import sys
import logging
import json

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("verify_migration")

# Importer la classe ApifyScraper qui devrait maintenant utiliser la nouvelle implémentation
try:
    from agents.scraper.apify_scraper import ApifyScraper
    logger.info("✅ Import de ApifyScraper réussi")
except ImportError as e:
    logger.error(f"❌ Erreur lors de l'importation: {str(e)}")
    sys.exit(1)

def verify_implementation():
    """Vérifie que l'implémentation utilisée est bien la nouvelle"""
    
    # Créer une instance du scraper
    scraper = ApifyScraper()
    
    # Vérifier le nom de la classe réelle (devrait être ApifyClientScraper)
    class_name = scraper.__class__.__name__
    orig_class = scraper.__class__.__module__ + "." + class_name
    
    logger.info(f"Classe utilisée: {class_name} (de {orig_class})")
    
    if class_name == "ApifyClientScraper":
        logger.info("✅ La NOUVELLE implémentation est utilisée!")
        
        # Vérifier que la méthode run existe
        if hasattr(scraper, "run") and callable(getattr(scraper, "run")):
            logger.info("✅ La méthode 'run' est disponible")
        else:
            logger.error("❌ La méthode 'run' n'est pas disponible")
            return False
        
        # Tester avec un petit exemple en mode simulation
        test_input = {
            "niche": "test_restaurant",
            "campaign_id": "verify_migration_test",
            "params": {
                "locationQuery": "Paris, FR",
                "maxCrawledPlacesPerSearch": 3
            }
        }
        
        # Forcer le mode simulation pour ne pas consommer de crédits API
        scraper.use_simulation = True
        logger.info("Test en mode simulation...")
        
        # Exécuter le test
        result = scraper.run(test_input)
        
        # Vérifier le résultat
        if "leads" in result and isinstance(result["leads"], list):
            leads_count = len(result["leads"])
            logger.info(f"✅ Test réussi! {leads_count} leads générés en simulation")
            
            # Afficher un exemple
            if leads_count > 0:
                example = result["leads"][0]
                logger.info(f"Exemple de lead: {example.get('company_name')}")
            
            # Sauvegarder le résultat pour référence
            with open("verify_migration_result.json", "w") as f:
                json.dump(result, f, indent=2)
            
            return True
        else:
            logger.error("❌ Le test a échoué - pas de leads générés")
            return False
    else:
        logger.error(f"❌ Mauvaise implémentation utilisée: {class_name}")
        return False

if __name__ == "__main__":
    logger.info("=== Vérification de la migration du scraper Apify ===")
    
    success = verify_implementation()
    
    if success:
        logger.info("\n✅ MIGRATION RÉUSSIE - Le système utilise correctement la nouvelle implémentation!")
        sys.exit(0)
    else:
        logger.error("\n❌ ÉCHEC DE LA MIGRATION - Des problèmes ont été détectés")
        sys.exit(1)
