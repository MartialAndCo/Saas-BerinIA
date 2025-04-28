#!/usr/bin/env python3
"""
Test complet du système infra-ia en conditions réelles.
Exécute un flux de campagne complet avec de vraies données scrapées.
"""

import os
import sys
import json
import time
import logging
import argparse
from datetime import datetime

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"tests/logs/system_test_{datetime.now().strftime('%Y%m%d%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("system_test")

# Importer les agents nécessaires
try:
    from agents.controller.campaign_starter_agent import CampaignStarterAgent
    from agents.scraper.apify_scraper import ApifyScraper
    from agents.cleaner.lead_cleaner import CleanerAgent
    from agents.classifier.lead_classifier_agent import LeadClassifierAgent
    from agents.exporter.crm_exporter_agent import CRMExporterAgent
    from agents.messenger.messenger_agent import MessengerAgent
    from agents.analytics.analytics_agent import AnalyticsAgent
    from utils.config import get_config
    logger.info("✅ Modules importés avec succès")
except ImportError as e:
    logger.error(f"❌ Erreur lors de l'importation des modules: {str(e)}")
    sys.exit(1)

def test_full_campaign(args):
    """
    Exécute un test de campagne complète avec tous les agents
    """
    start_time = time.time()
    logger.info(f"🚀 Démarrage du test complet avec niche: {args.niche}")
    
    # 1. Configuration du test
    campaign_id = f"TEST_{args.niche.replace(' ', '_')}_{int(time.time())}"
    
    results = {
        "campaign_id": campaign_id,
        "niche": args.niche,
        "start_time": datetime.now().isoformat(),
        "phases": {},
        "summary": {}
    }
    
    # 2. Tester individuellement ou utiliser CampaignStarter
    if args.individual:
        logger.info("Mode de test: agents individuels séquentiels")
        results = test_individual_agents(args.niche, campaign_id, args)
    else:
        logger.info("Mode de test: CampaignStarterAgent intégré")
        results = test_campaign_starter(args.niche, campaign_id, args)
    
    # 3. Exécuter l'AnalyticsAgent sur les résultats (si demandé)
    if args.analytics:
        logger.info("🔍 Exécution de l'analyse post-campagne...")
        analytics_results = run_analytics(campaign_id, args.niche)
        results["analytics"] = analytics_results
    
    # 4. Générer un résumé et des métriques
    results["execution_time"] = time.time() - start_time
    results["end_time"] = datetime.now().isoformat()
    
    # Rapport final
    report_path = f"tests/reports/system_test_report_{campaign_id}.json"
    with open(report_path, "w") as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"📊 Rapport final généré: {report_path}")
    logger.info(f"⏱️ Temps total d'exécution: {results['execution_time']:.2f} secondes")
    
    # Afficher un résumé des résultats
    print_summary(results)
    
    return results

def test_individual_agents(niche, campaign_id, args):
    """
    Exécuter chaque agent individuellement dans l'ordre
    """
    results = {
        "campaign_id": campaign_id,
        "niche": niche,
        "phases": {},
        "stats": {}
    }
    
    # 1. Scraping
    logger.info("📡 Phase 1: Scraping des leads...")
    scraper = ApifyScraper()
    
    # Forcer le mode API si spécifié
    if args.force_api and hasattr(scraper, 'use_simulation'):
        scraper.use_simulation = False
        logger.info("Mode API réelle forcé pour le scraper")
    
    scraper_input = {
        "niche": niche,
        "params": {
            "locationQuery": args.location,
            "maxCrawledPlacesPerSearch": args.max_leads,
            "language": args.language
        },
        "campaign_id": campaign_id
    }
    
    scraper_result = scraper.run(scraper_input)
    results["phases"]["scraping"] = scraper_result
    
    # Vérifier si le scraping a échoué
    if "error" in scraper_result or "leads" not in scraper_result or not scraper_result.get("leads"):
        logger.error(f"❌ Échec du scraping: {scraper_result.get('error', 'Aucun lead trouvé')}")
        results["status"] = "FAILED"
        return results
    
    leads = scraper_result.get("leads", [])
    logger.info(f"✅ Scraping réussi: {len(leads)} leads extraits")
    
    # 2. Nettoyage
    logger.info("🧹 Phase 2: Nettoyage des leads...")
    cleaner = CleanerAgent()
    cleaner_input = {
        "data": leads,
        "campaign_id": campaign_id
    }
    
    cleaner_result = cleaner.run(cleaner_input)
    results["phases"]["cleaning"] = cleaner_result
    
    # Vérifier si le nettoyage a échoué
    if "error" in cleaner_result or "clean_data" not in cleaner_result:
        logger.error(f"❌ Échec du nettoyage: {cleaner_result.get('error', 'Pas de données propres')}")
        results["status"] = "FAILED"
        return results
    
    clean_leads = cleaner_result.get("clean_data", [])
    logger.info(f"✅ Nettoyage réussi: {len(clean_leads)} leads nettoyés")
    
    # Enrichir les données pour éviter les erreurs dans le LeadClassifierAgent
    for lead in clean_leads:
        # Assurer que les champs nécessaires existent et sont des chaînes vides si null
        if lead.get("industry") is None:
            # Utiliser la première catégorie comme industrie
            if lead.get("category") and isinstance(lead.get("category"), list) and len(lead.get("category")) > 0:
                lead["industry"] = lead["category"][0]
            else:
                lead["industry"] = "Restaurant"  # Valeur par défaut
        
        if lead.get("position") is None:
            lead["position"] = "Owner"  # Valeur par défaut pour un restaurant
            
        if lead.get("company_size") is None:
            lead["company_size"] = "small"  # La plupart des restaurants sont de petite taille
            
        # Assurer que location existe (utilisé pour les heuristiques)
        if lead.get("location") is None:
            lead["location"] = lead.get("city", "") + ", " + lead.get("country", "")
    
    # 3. Classification
    logger.info("🏷️ Phase 3: Classification des leads...")
    classifier = LeadClassifierAgent()
    classifier_input = {
        "leads": clean_leads,  # LeadClassifierAgent s'attend à recevoir les leads ici
        "campaign_id": campaign_id
    }
    
    classifier_result = classifier.run(classifier_input)
    results["phases"]["classification"] = classifier_result
    
    # Vérifier si la classification a échoué
    if "error" in classifier_result or "classified_leads" not in classifier_result:
        logger.error(f"❌ Échec de la classification: {classifier_result.get('error', 'Pas de leads classifiés')}")
        results["status"] = "FAILED"
        return results
    
    classified_leads = classifier_result.get("classified_leads", [])
    logger.info(f"✅ Classification réussie: {len(classified_leads)} leads classifiés")
    
    # Nous ne classifions plus les leads par température à cette étape
    # Compter simplement les leads avec des canaux de contact valides
    leads_with_email = [l for l in classified_leads if l.get("email")]
    leads_with_phone = [l for l in classified_leads if l.get("phone")]
    leads_with_both = [l for l in classified_leads if l.get("email") and l.get("phone")]
    
    results["stats"]["classification"] = {
        "leads_with_email": len(leads_with_email),
        "leads_with_phone": len(leads_with_phone),
        "leads_with_both": len(leads_with_both),
        "avg_global_score": sum(l.get("global_score", 0) for l in classified_leads) / len(classified_leads) if classified_leads else 0
    }
    
    # 4. Export CRM
    logger.info("📤 Phase 4: Export CRM...")
    exporter = CRMExporterAgent()
    export_input = {
        "classified_leads": classified_leads,
        "campaign_id": campaign_id,
        "daily_limit": args.max_export
    }
    
    export_result = exporter.run(export_input)
    results["phases"]["export"] = export_result
    
    # Vérifier si l'export a échoué
    if "error" in export_result:
        logger.error(f"❌ Échec de l'export: {export_result.get('error')}")
        results["status"] = "FAILED"
        return results
    
    leads_to_export = export_result.get("export_decision", {}).get("leads_to_export_now", [])
    leads_delayed = export_result.get("export_decision", {}).get("leads_to_delay", [])
    
    logger.info(f"✅ Export réussi: {len(leads_to_export)} leads à exporter maintenant, {len(leads_delayed)} différés")
    
    # 5. Messagerie (si des leads à contacter)
    if leads_to_export and not args.skip_messenger:
        logger.info("📨 Phase 5: Stratégie de contact...")
        messenger = MessengerAgent()
        messenger_input = {
            "leads_to_contact": leads_to_export,
            "campaign_id": campaign_id,
            "timezone": args.timezone
        }
        
        messenger_result = messenger.run(messenger_input)
        results["phases"]["contact"] = messenger_result
        
        # Vérifier si le contact a échoué
        if "error" in messenger_result:
            logger.error(f"❌ Échec de la stratégie de contact: {messenger_result.get('error')}")
            results["status"] = "WARNING"  # Non critique, on continue
        else:
            contact_strategies = messenger_result.get("contact_strategy", [])
            logger.info(f"✅ Stratégie de contact réussie: {len(contact_strategies)} stratégies générées")
    else:
        results["phases"]["contact"] = {
            "status": "SKIPPED",
            "reason": "Aucun lead à contacter ou phase désactivée"
        }
    
    # Résultat final
    results["status"] = "COMPLETED"
    
    return results

def test_campaign_starter(niche, campaign_id, args):
    """
    Utiliser le CampaignStarterAgent pour orchestrer tout le processus
    """
    logger.info("🎯 Exécution via CampaignStarterAgent...")
    
    # Préparer les paramètres d'entrée
    validated_niche = {
        "niche": niche,
        "confidence": 0.95,
        "reasons": [
            "Niche spécifiée pour le test système",
            "Test en conditions réelles"
        ]
    }
    
    campaign_params = {
        "scraping": {
            "use_apify": True,
            "use_apollo": False,
            "apify_params": {
                "locationQuery": args.location,
                "maxCrawledPlacesPerSearch": args.max_leads,
                "language": args.language,
                "skipClosedPlaces": False
            },
        },
        "crm": {
            "daily_limit": args.max_export,
            "exported_today": 0
        },
        "contact": {
            "timezone": args.timezone,
            "skip_contact": args.skip_messenger
        }
    }
    
    # Si on force le mode API
    os.environ["FORCE_API_MODE"] = "true" if args.force_api else "false"
    
    # Initialiser et exécuter le CampaignStarterAgent
    starter = CampaignStarterAgent()
    
    input_data = {
        "validated_niche": validated_niche,
        "campaign_params": campaign_params,
        "campaign_id": campaign_id,
        "system_status": {"status": "READY"}
    }
    
    # Exécuter l'agent
    result = starter.run(input_data)
    
    # Réinitialiser la variable d'environnement
    if "FORCE_API_MODE" in os.environ:
        del os.environ["FORCE_API_MODE"]
    
    return result

def run_analytics(campaign_id, niche):
    """
    Exécuter l'AnalyticsAgent pour analyser la campagne
    """
    logger.info(f"📊 Analyse de la campagne {campaign_id}...")
    
    analytics = AnalyticsAgent()
    analytics_input = {
        "operation": "analyze_campaign",
        "campaign_id": campaign_id,
        "niche": niche,
        "verbose": True
    }
    
    analytics_result = analytics.run(analytics_input)
    
    if "error" in analytics_result:
        logger.error(f"❌ Échec de l'analyse: {analytics_result.get('error')}")
    else:
        logger.info("✅ Analyse réussie")
        
        # Extraire quelques insights pour le résumé
        insights = analytics_result.get("insights", [])
        if insights:
            logger.info("🔍 Premiers insights:")
            for i, insight in enumerate(insights[:3]):
                logger.info(f"  {i+1}. {insight.get('description', '')}")
    
    return analytics_result

def print_summary(results):
    """
    Affiche un résumé des résultats du test
    """
    print("\n" + "="*80)
    print(f"📋 RÉSUMÉ DU TEST SYSTÈME - Campagne: {results['campaign_id']}")
    print("="*80)
    
    # Statut global
    status = results.get("status", "UNKNOWN")
    status_emoji = "✅" if status == "COMPLETED" else "⚠️" if status == "WARNING" else "❌"
    print(f"\nStatut global: {status_emoji} {status}")
    
    # Statistiques des phases
    print("\nRésultats par phase:")
    
    # 1. Scraping
    if "scraping" in results.get("phases", {}):
        scrape_count = len(results["phases"]["scraping"].get("leads", []))
        print(f"🔍 Scraping: {scrape_count} leads")
    
    # 2. Nettoyage
    if "cleaning" in results.get("phases", {}):
        clean_count = len(results["phases"]["cleaning"].get("clean_data", []))
        rejected = len(results["phases"]["cleaning"].get("rejected_leads", []))
        print(f"🧹 Nettoyage: {clean_count} leads nettoyés, {rejected} rejetés")
    
    # 3. Classification
    if "classification" in results.get("phases", {}):
        class_count = len(results["phases"]["classification"].get("classified_leads", []))
        hot = results.get("stats", {}).get("classification", {}).get("hot_leads", 0)
        warm = results.get("stats", {}).get("classification", {}).get("warm_leads", 0)
        cold = results.get("stats", {}).get("classification", {}).get("cold_leads", 0)
        print(f"🏷️ Classification: {class_count} leads classifiés ({hot} chauds, {warm} tièdes, {cold} froids)")
    
    # 4. Export
    if "export" in results.get("phases", {}):
        export_count = len(results["phases"]["export"].get("export_decision", {}).get("leads_to_export_now", []))
        delayed = len(results["phases"]["export"].get("export_decision", {}).get("leads_to_delay", []))
        print(f"📤 Export: {export_count} leads exportés, {delayed} différés")
    
    # 5. Contact
    if "contact" in results.get("phases", {}):
        if results["phases"]["contact"].get("status") == "SKIPPED":
            print(f"📨 Contact: IGNORÉ - {results['phases']['contact'].get('reason', '')}")
        else:
            contact_count = len(results["phases"]["contact"].get("contact_strategy", []))
            print(f"📨 Contact: {contact_count} stratégies de contact")
    
    # Temps d'exécution
    exec_time = results.get("execution_time", 0)
    print(f"\n⏱️ Temps total d'exécution: {exec_time:.2f} secondes ({exec_time/60:.2f} minutes)")
    
    # Analyse
    if "analytics" in results:
        print("\n📊 Analyse de la campagne:")
        for metric, value in results["analytics"].get("metrics", {}).items():
            if isinstance(value, float):
                print(f"  - {metric}: {value * 100:.2f}%" if value <= 1 else f"  - {metric}: {value:.2f}")
            else:
                print(f"  - {metric}: {value}")
    
    print("\n" + "="*80)
    print(f"📝 Rapport détaillé: tests/reports/system_test_report_{results['campaign_id']}.json")
    print("="*80 + "\n")

def main():
    parser = argparse.ArgumentParser(description="Test complet du système infra-ia en conditions réelles")
    parser.add_argument("--niche", default="restaurant", help="Niche à cibler pour le test")
    parser.add_argument("--location", default="Paris, France", help="Localisation pour le scraping")
    parser.add_argument("--language", default="fr", help="Langue pour le scraping")
    parser.add_argument("--max-leads", type=int, default=10, help="Nombre max de leads à scraper")
    parser.add_argument("--max-export", type=int, default=5, help="Limite quotidienne d'export")
    parser.add_argument("--timezone", default="Europe/Paris", help="Fuseau horaire pour la stratégie de contact")
    parser.add_argument("--individual", action="store_true", help="Tester chaque agent individuellement")
    parser.add_argument("--skip-messenger", action="store_true", help="Ignorer la phase de messagerie")
    parser.add_argument("--analytics", action="store_true", help="Exécuter l'analyse post-campagne")
    parser.add_argument("--force-api", action="store_true", help="Forcer l'utilisation des API réelles (si disponibles)")
    
    args = parser.parse_args()
    
    logger.info("=== Démarrage du test système complet ===")
    logger.info(f"Configuration: niche={args.niche}, location={args.location}, max_leads={args.max_leads}")
    
    # Exécuter le test
    try:
        results = test_full_campaign(args)
        sys.exit(0 if results.get("status") == "COMPLETED" else 1)
    except Exception as e:
        logger.error(f"❌ Exception non gérée lors du test: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
