#!/usr/bin/env python3
"""
Script de test pour le scraper Apify utilisant la bibliothèque cliente officielle.
Vérifie le fonctionnement avec l'API réelle ou en mode simulation.
"""
import os
import sys
import json
import logging
import argparse
from datetime import datetime

# Configurer le logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("apify_client_test")

# Importer les modules nécessaires
try:
    from agents.scraper.apify_client_scraper import ApifyClientScraper, APIFY_CLIENT_AVAILABLE
    from utils.config import get_config
    logger.info("Modules importés avec succès")
except ImportError as e:
    logger.error(f"Erreur lors de l'importation des modules: {str(e)}")
    sys.exit(1)

def test_apify_connection():
    """Teste la connexion à l'API Apify"""
    logger.info("Test de la connexion à l'API Apify...")
    
    config = get_config()
    
    # Vérifier si le client est disponible
    if not APIFY_CLIENT_AVAILABLE:
        logger.error("❌ Module apify-client non installé")
        return False
    
    # Vérifier si une clé API est disponible
    api_key = config.get_apify_api_key()
    if not api_key:
        logger.warning("❌ Aucune clé API Apify configurée. Mode simulation uniquement.")
        return False
    
    # Initialiser le scraper avec la clé API
    scraper = ApifyClientScraper(api_token=api_key)
    
    # Vérifier si le mode simulation est désactivé
    if scraper.use_simulation:
        logger.warning("❌ Clé API Apify invalide. Mode simulation activé.")
        return False
    
    logger.info("✅ Clé API Apify valide et configurée correctement.")
    return True

def test_restaurant_scraping_simulation():
    """Teste le scraping des restaurants en mode simulation"""
    logger.info("Test du scraping de restaurants (simulation)...")
    
    # Forcer le mode simulation
    scraper = ApifyClientScraper()
    scraper.use_simulation = True
    
    # Définir les paramètres de recherche
    input_data = {
        "niche": "restaurant",
        "campaign_id": "test_campaign",
        "params": {
            "language": "fr",
            "locationQuery": "Paris, FR", 
            "maxCrawledPlacesPerSearch": 10,
            "searchStringsArray": ["restaurant"],
            "skipClosedPlaces": False
        }
    }
    
    # Exécuter le scraping
    try:
        result = scraper.run(input_data)
        
        # Vérifier le résultat
        if not result or "error" in result:
            logger.error(f"❌ Erreur lors du scraping: {result.get('error') if result else 'Résultat vide'}")
            return False
        
        # Vérifier que des leads ont été extraits
        leads_count = len(result.get("leads", []))
        if leads_count == 0:
            logger.error("❌ Aucun lead extrait.")
            return False
        
        logger.info(f"✅ Simulation de scraping réussie. {leads_count} leads extraits.")
        
        # Afficher quelques leads d'exemple
        if leads_count > 0:
            logger.info("Exemples de leads:")
            for i, lead in enumerate(result["leads"][:3]):
                logger.info(f"  Lead {i+1}: {lead['company_name']} - {lead.get('phone')} - {lead.get('email')}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Exception lors du test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_apify_live_api():
    """Teste l'API Apify réelle en utilisant la bibliothèque cliente officielle"""
    logger.info("Test de l'API Apify réelle...")
    
    # Vérifier si le client est disponible
    if not APIFY_CLIENT_AVAILABLE:
        logger.warning("⚠️ Module apify-client non installé, impossible de tester l'API réelle.")
        return None
    
    config = get_config()
    api_key = config.get_apify_api_key()
    
    if not api_key:
        logger.warning("⚠️ Pas de clé API configurée, impossible de tester l'API réelle.")
        return None
    
    scraper = ApifyClientScraper(api_token=api_key)
    
    # Si toujours en mode simulation malgré la clé, il y a un problème
    if scraper.use_simulation:
        logger.warning("⚠️ Mode simulation actif malgré la clé API, problème de configuration.")
        return False
    
    # Définir les paramètres de recherche
    input_data = {
        "niche": "restaurant",
        "campaign_id": "test_campaign_live",
        "params": {
            "language": "fr",
            "locationQuery": "Paris, FR", 
            "maxCrawledPlacesPerSearch": 5,  # Limiter pour les tests
            "searchStringsArray": ["restaurant"],
            "skipClosedPlaces": False
        }
    }
    
    # Exécuter le scraping avec l'API réelle
    try:
        logger.info("Appel de l'API Apify réelle (peut prendre quelques minutes)...")
        result = scraper.run(input_data)
        
        # Vérifier le résultat
        if not result or "error" in result:
            logger.error(f"❌ Erreur lors du scraping réel: {result.get('error') if result else 'Résultat vide'}")
            return False
        
        # Vérifier que des leads ont été extraits
        leads_count = len(result.get("leads", []))
        if leads_count == 0:
            logger.error("❌ Aucun lead extrait depuis l'API réelle.")
            return False
        
        logger.info(f"✅ Scraping réel réussi. {leads_count} leads extraits via l'API Apify.")
        
        # Afficher quelques leads d'exemple
        if leads_count > 0:
            logger.info("Exemples de leads réels:")
            for i, lead in enumerate(result["leads"][:3]):
                logger.info(f"  Lead {i+1}: {lead['company_name']} - {lead.get('city')} - {lead.get('rating', 'N/A')}")
        
        # Sauvegarder le résultat réel pour analyse
        with open("apify_real_result.json", "w") as f:
            json.dump(result, f, indent=2)
            logger.info("Résultat sauvegardé dans 'apify_real_result.json'")
        
        return True
    except Exception as e:
        logger.error(f"❌ Exception lors du test réel: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def run_tests(args):
    """Exécute les tests du scraper"""
    results = {}
    
    # Tester la connexion à l'API Apify
    results["apify_connection"] = test_apify_connection()
    
    # Tester le scraping simulé
    results["simulated_scraping"] = test_restaurant_scraping_simulation()
    
    # Tester l'API réelle si demandé
    if args.live_api:
        results["live_api"] = test_apify_live_api()
    
    # Afficher le résumé
    logger.info("\n=== Résumé des tests ===")
    all_pass = True
    
    for test_name, result in results.items():
        if result is None:
            status = "⚠️ IGNORÉ"
        else:
            status = "✅ RÉUSSI" if result else "❌ ÉCHOUÉ"
            if not result and result is not None:
                all_pass = False
                
        logger.info(f"{test_name}: {status}")
    
    # Conseils de configuration
    if not APIFY_CLIENT_AVAILABLE:
        logger.info("\n=== Conseils d'installation ===")
        logger.info("- Installez le client officiel Apify avec: pip install apify-client")
    
    if not results.get("apify_connection", False):
        logger.info("\n=== Conseils de configuration ===")
        logger.info("- Pour configurer l'API Apify:")
        logger.info("  1. Créez un compte sur apify.com")
        logger.info("  2. Obtenez une clé API depuis https://console.apify.com/account/integrations")
        logger.info("  3. Ajoutez la clé dans config/.env: APIFY_API_KEY=votre_clé_api")
    
    return all_pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test du scraper Apify avec client officiel")
    parser.add_argument("--live-api", action="store_true", help="Tester l'API Apify réelle (nécessite une clé API)")
    args = parser.parse_args()
    
    logger.info("=== Test du scraper Apify avec client officiel ===")
    success = run_tests(args)
    
    if success:
        logger.info("Tous les tests ont réussi!")
        sys.exit(0)
    else:
        logger.error("Certains tests ont échoué.")
        sys.exit(1)
