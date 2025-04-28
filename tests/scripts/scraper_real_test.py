#!/usr/bin/env python3
"""
Script de test réel pour le scraper Apify avec client officiel.
Compare les performances et résultats entre l'ancienne et la nouvelle implémentation.
"""

import os
import sys
import json
import time
import logging
import argparse
from datetime import datetime

# Configurer le logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("scraper_real_test")

# Importer les modules nécessaires
try:
    from agents.scraper.apify_scraper import ApifyScraper
    from agents.scraper.apify_client_scraper import ApifyClientScraper, APIFY_CLIENT_AVAILABLE
    from utils.config import get_config
    logger.info("Modules importés avec succès")
except ImportError as e:
    logger.error(f"Erreur lors de l'importation des modules: {str(e)}")
    sys.exit(1)

def test_scrapers_real_data(niche="restaurant", location="Paris, FR", max_results=10):
    """
    Teste les deux implémentations de scraper sur des données réelles et compare les résultats
    
    Args:
        niche: La niche à rechercher
        location: L'emplacement à rechercher
        max_results: Nombre maximum de résultats à extraire
    """
    logger.info(f"Test de scraping réel pour la niche: {niche} à {location}")
    
    # Paramètres communs pour les deux scrapers
    params = {
        "niche": niche,
        "campaign_id": "real_test_comparison",
        "params": {
            "language": "fr",
            "locationQuery": location, 
            "maxCrawledPlacesPerSearch": max_results,
            "searchStringsArray": [niche],
            "skipClosedPlaces": False
        }
    }
    
    # Vérifier la disponibilité du client Apify
    if not APIFY_CLIENT_AVAILABLE:
        logger.error("❌ Le client Apify n'est pas disponible. Installez-le avec: pip install apify-client")
        return False
    
    # Vérifier la clé API
    config = get_config()
    api_key = config.get_apify_api_key()
    if not api_key:
        logger.warning("⚠️ Pas de clé API Apify configurée, test en mode simulation uniquement.")
    
    # ====== Test de l'ancienne implémentation ======
    logger.info("\n=== Test de l'ANCIENNE implémentation (ApifyScraper) ===")
    
    old_scraper = ApifyScraper(api_token=api_key)
    old_simulation = old_scraper.use_simulation
    
    logger.info(f"Mode: {'SIMULATION' if old_simulation else 'API RÉELLE'}")
    
    old_start_time = time.time()
    try:
        old_result = old_scraper.run(params)
        old_duration = time.time() - old_start_time
        
        old_success = "error" not in old_result
        old_leads_count = len(old_result.get("leads", []))
        
        logger.info(f"Résultat: {'✅ SUCCÈS' if old_success else '❌ ÉCHEC'}")
        logger.info(f"Nombre de leads: {old_leads_count}")
        logger.info(f"Durée: {old_duration:.2f} secondes")
        
        if old_leads_count > 0:
            logger.info("Exemples de leads:")
            for i, lead in enumerate(old_result.get("leads", [])[:3]):
                logger.info(f"  Lead {i+1}: {lead.get('company_name')} - {lead.get('phone')} - {lead.get('city')}")
        
        # Sauvegarder les résultats pour analyse
        with open("old_scraper_results.json", "w") as f:
            json.dump(old_result, f, indent=2)
            logger.info("Résultats sauvegardés dans 'old_scraper_results.json'")
    
    except Exception as e:
        logger.error(f"❌ Exception lors du test de l'ancienne implémentation: {str(e)}")
        import traceback
        traceback.print_exc()
        old_success = False
        old_duration = time.time() - old_start_time
        old_leads_count = 0
    
    # ====== Test de la nouvelle implémentation ======
    logger.info("\n=== Test de la NOUVELLE implémentation (ApifyClientScraper) ===")
    
    new_scraper = ApifyClientScraper(api_token=api_key)
    new_simulation = new_scraper.use_simulation
    
    logger.info(f"Mode: {'SIMULATION' if new_simulation else 'API RÉELLE'}")
    
    new_start_time = time.time()
    try:
        new_result = new_scraper.run(params)
        new_duration = time.time() - new_start_time
        
        new_success = "error" not in new_result
        new_leads_count = len(new_result.get("leads", []))
        
        logger.info(f"Résultat: {'✅ SUCCÈS' if new_success else '❌ ÉCHEC'}")
        logger.info(f"Nombre de leads: {new_leads_count}")
        logger.info(f"Durée: {new_duration:.2f} secondes")
        
        if new_leads_count > 0:
            logger.info("Exemples de leads:")
            for i, lead in enumerate(new_result.get("leads", [])[:3]):
                logger.info(f"  Lead {i+1}: {lead.get('company_name')} - {lead.get('phone')} - {lead.get('city')}")
        
        # Sauvegarder les résultats pour analyse
        with open("new_scraper_results.json", "w") as f:
            json.dump(new_result, f, indent=2)
            logger.info("Résultats sauvegardés dans 'new_scraper_results.json'")
    
    except Exception as e:
        logger.error(f"❌ Exception lors du test de la nouvelle implémentation: {str(e)}")
        import traceback
        traceback.print_exc()
        new_success = False
        new_duration = time.time() - new_start_time
        new_leads_count = 0
    
    # ====== Comparaison des résultats ======
    logger.info("\n=== Comparaison des résultats ===")
    
    # Format de sortie pour tableau
    header = f"| {'Métrique':<20} | {'Ancienne implémentation':<25} | {'Nouvelle implémentation':<25} |"
    separator = f"|{'-'*22}|{'-'*27}|{'-'*27}|"
    
    logger.info(separator)
    logger.info(header)
    logger.info(separator)
    logger.info(f"| {'Mode':<20} | {('SIMULATION' if old_simulation else 'API RÉELLE'):<25} | {('SIMULATION' if new_simulation else 'API RÉELLE'):<25} |")
    logger.info(f"| {'Statut':<20} | {('SUCCÈS' if old_success else 'ÉCHEC'):<25} | {('SUCCÈS' if new_success else 'ÉCHEC'):<25} |")
    logger.info(f"| {'Nombre de leads':<20} | {str(old_leads_count):<25} | {str(new_leads_count):<25} |")
    logger.info(f"| {'Durée (secondes)':<20} | {str(round(old_duration, 2)):<25} | {str(round(new_duration, 2)):<25} |")
    logger.info(separator)
    
    performance_improvement = ((old_duration - new_duration) / old_duration) * 100 if old_duration > 0 else 0
    logger.info(f"Amélioration des performances: {performance_improvement:.2f}%")
    
    # Recommandation
    logger.info("\n=== Recommandation ===")
    if new_success and (not old_success or new_leads_count >= old_leads_count):
        logger.info("✅ La NOUVELLE implémentation est RECOMMANDÉE pour un déploiement complet.")
        if new_leads_count > old_leads_count:
            logger.info(f"   Amélioration de la qualité: +{new_leads_count - old_leads_count} leads supplémentaires")
        if performance_improvement > 0:
            logger.info(f"   Amélioration des performances: {performance_improvement:.2f}% plus rapide")
        
        return True
    elif old_success and new_success:
        logger.info("⚠️ Les deux implémentations fonctionnent, mais l'ancienne semble donner de meilleurs résultats.")
        logger.info("   Recommandation: Examiner les différences dans les résultats et améliorer la nouvelle implémentation.")
        return False
    else:
        logger.info("❌ Des problèmes ont été détectés. Correction nécessaire avant déploiement.")
        if not new_success:
            logger.info("   La nouvelle implémentation a échoué.")
        return False

def main():
    parser = argparse.ArgumentParser(description="Test réel des scrapers Apify")
    parser.add_argument("--niche", default="restaurant", help="Niche à rechercher")
    parser.add_argument("--location", default="Paris, FR", help="Emplacement à rechercher")
    parser.add_argument("--max", type=int, default=10, help="Nombre maximum de résultats")
    args = parser.parse_args()
    
    logger.info("=== Test réel des scrapers Apify ===")
    success = test_scrapers_real_data(args.niche, args.location, args.max)
    
    # Proposer la substitution
    if success:
        logger.info("\n=== Comment réaliser la substitution ===")
        logger.info("1. Renommer 'apify_scraper.py' en 'apify_scraper_old.py'")
        logger.info("2. Renommer 'apify_client_scraper.py' en 'apify_scraper.py'")
        logger.info("3. Importer 'ApifyClientScraper as ApifyScraper' dans le nouveau fichier")
        
        # Créer un script de migration
        migration_script = """#!/bin/bash
echo "Migration du scraper Apify vers la nouvelle implémentation..."
cd /root/infra-ia/agents/scraper/
mv apify_scraper.py apify_scraper_old.py
cp apify_client_scraper.py apify_scraper.py
sed -i '1i# Nouvelle implémentation renommée pour compatibilité\\nfrom agents.scraper.apify_client_scraper import ApifyClientScraper as ApifyScraper\\n# Le reste du fichier est conservé pour référence\\n\\n\"\"\"\\nANCIENNE IMPLÉMENTATION - CONSERVÉE POUR RÉFÉRENCE\\n\"\"\"\\n' apify_scraper.py
echo "Migration terminée. L'ancienne implémentation a été conservée dans apify_scraper_old.py"
"""
        with open("migrate_apify_scraper.sh", "w") as f:
            f.write(migration_script)
        os.chmod("migrate_apify_scraper.sh", 0o755)
        
        logger.info("4. SCRIPT AUTOMATIQUE CRÉÉ: './migrate_apify_scraper.sh'")
    
    logger.info("\nTest terminé!")
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
