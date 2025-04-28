#!/usr/bin/env python3
"""
Script de démarrage et de test du DecisionBrainAgent.
Ce script permet de lancer l'agent cerveau du système de manière isolée
pour observer son fonctionnement et ses décisions stratégiques.
"""

import os
import sys
import time
import json
import argparse
import logging
from datetime import datetime

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"logs/brain_test_{datetime.now().strftime('%Y%m%d%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("brain_test")

# Importer notre système de logging amélioré
try:
    from logs.enhanced_logger import get_agent_logger, log_system_execution
    logger.info("✅ Système de logging amélioré chargé")
except ImportError as e:
    logger.warning(f"⚠️ Système de logging standard utilisé: {str(e)}")

# Importer l'agent cerveau et autres agents requis
try:
    from agents.controller.decision_brain_agent import DecisionBrainAgent
    from agents.classifier.lead_classifier_agent import LeadClassifierAgent
    from agents.exporter.crm_exporter_agent import CRMExporterAgent
    from agents.cleaner.lead_cleaner import CleanerAgent
    logger.info("✅ Agents importés avec succès")
except ImportError as e:
    logger.error(f"❌ Erreur lors de l'importation des agents: {str(e)}")
    sys.exit(1)

# Vérifier l'intégration Berinia
try:
    from integrations.berinia.db_connector import test_berinia_connection
    berinia_available = test_berinia_connection()
    logger.info(f"✅ Intégration Berinia testée - Disponible: {berinia_available}")
except ImportError as e:
    logger.warning(f"⚠️ Intégration Berinia non disponible: {str(e)}")
    berinia_available = False

def run_brain_agent(args):
    """Exécute le DecisionBrainAgent avec les paramètres fournis"""
    logger.info("🚀 Démarrage du DecisionBrainAgent...")

    # Initialiser l'agent avec le système de logging amélioré si disponible
    brain_logger = get_agent_logger("DecisionBrainAgent") if 'get_agent_logger' in globals() else None
    brain = DecisionBrainAgent()
    logger.info("🧠 DecisionBrainAgent initialisé")

    # Préparer les données d'entrée
    input_data = {
        "operation": args.operation,
        "context": {
            "test_mode": args.test_mode,
            "simulate_data": args.simulate,
            "verbose": args.verbose,
            "integration_tests": args.integration_tests,
            "berinia_available": berinia_available
        }
    }

    # Si des données supplémentaires sont fournies
    if args.input_file:
        try:
            with open(args.input_file, 'r') as f:
                additional_data = json.load(f)
                input_data.update(additional_data)
                logger.info(f"📥 Données d'entrée chargées depuis {args.input_file}")
        except Exception as e:
            logger.warning(f"⚠️ Impossible de charger les données depuis {args.input_file}: {str(e)}")

    # Exécuter l'agent
    start_time = time.time()
    agent_flow = [{
        "agent": "DecisionBrainAgent", 
        "start_time": datetime.now().isoformat()
    }]
    
    try:
        logger.info("⏳ Exécution de l'agent cerveau en cours...")
        if brain_logger:
            brain_logger.log_input(input_data)
            brain_logger.log_processing("Exécution du DecisionBrainAgent démarrée")
            
        result = brain.run(input_data)
        execution_time = time.time() - start_time
        logger.info(f"✅ Agent exécuté avec succès en {execution_time:.2f} secondes")
        
        if brain_logger:
            brain_logger.log_output(result)
            brain_logger.log_completion("success")

        # Tests d'intégration si demandé
        if args.integration_tests:
            logger.info("🔄 Exécution des tests d'intégration...")
            integration_results = run_integration_tests(input_data, result)
            result["integration_tests"] = integration_results
            
            # Mise à jour de l'agent flow
            for test in integration_results:
                agent_flow.append({
                    "agent": test.get("agent", "UnknownAgent"),
                    "start_time": test.get("start_time"),
                    "end_time": test.get("end_time"),
                    "status": test.get("status")
                })

        # Sauvegarder le résultat
        result_file = f"logs/brain_result_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
        with open(result_file, 'w') as f:
            json.dump(result, f, indent=2)
        logger.info(f"💾 Résultat sauvegardé dans {result_file}")
        
        # Enregistrer le flux d'exécution complet
        if 'log_system_execution' in globals():
            system_log = log_system_execution(agent_flow, result, None)
            logger.info(f"📊 Rapport d'exécution système: {system_log}")

        # Si mode verbeux, afficher plus de détails
        if args.verbose:
            logger.info("📊 Détails de la décision :")
            decision = result.get("decision", {})
            logger.info(f"  Action : {decision.get('action', 'non spécifiée')}")
            logger.info(f"  Campagne cible : {decision.get('campagne_cible', 'non spécifiée')}")
            logger.info(f"  Priorité : {decision.get('priorité', 'non spécifiée')}")
            logger.info(f"  Agents à impliquer : {', '.join(decision.get('agents_à_impliquer', []))}")

            # Afficher les étapes de réflexion
            logger.info("🧩 Étapes de réflexion :")
            for i, step in enumerate(result.get("thinking_steps", [])):
                logger.info(f"  {i+1}. {step}")

        return result

    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"❌ Erreur lors de l'exécution du DecisionBrainAgent: {str(e)}")
        logger.error(f"⏱️ Temps écoulé avant erreur: {execution_time:.2f} secondes")
        
        if brain_logger:
            brain_logger.log_error(e, {"execution_time": execution_time})
            brain_logger.log_completion("error")
            
        return {"error": str(e), "execution_time": execution_time}

def run_integration_tests(input_data, brain_result):
    """
    Effectue des tests d'intégration avec les autres agents du système
    pour vérifier le bon fonctionnement de bout en bout
    """
    test_results = []
    
    # Test avec quelques données factices pour la cohérence du test
    test_leads = [
        {
            "id": "test_lead_1",
            "company_name": "Entreprise Test 1",
            "email": "contact@test1.com",
            "phone": "+33123456789"
        },
        {
            "id": "test_lead_2",
            "company_name": "Entreprise Test 2",
            "email": "",  # Email vide pour tester la robustesse
            "phone": "+33987654321"
        },
        {
            "id": "test_lead_3",
            "company_name": "Entreprise Test 3",
            "email": "info@test3.fr",
            "phone": "+33555555555"
        }
    ]
    
    # 1. Test du CleanerAgent
    try:
        logger.info("🧪 Test du CleanerAgent...")
        cleaner_logger = get_agent_logger("CleanerAgent") if 'get_agent_logger' in globals() else None
        cleaner = CleanerAgent()
        
        cleaner_input = {
            "raw_leads": test_leads,
            "campaign_id": "test_campaign_123"
        }
        
        start_time = datetime.now()
        if cleaner_logger:
            cleaner_logger.log_input(cleaner_input)
            
        cleaner_result = cleaner.run(cleaner_input)
        end_time = datetime.now()
        
        if cleaner_logger:
            cleaner_logger.log_output(cleaner_result)
            cleaner_logger.log_completion("success")
            
        cleaned_leads = cleaner_result.get("cleaned_leads", [])
        logger.info(f"✅ CleanerAgent a traité {len(cleaned_leads)} leads")
        
        test_results.append({
            "agent": "CleanerAgent",
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "status": "success",
            "leads_processed": len(cleaned_leads)
        })
        
        # 2. Test du LeadClassifierAgent
        logger.info("🧪 Test du LeadClassifierAgent...")
        classifier_logger = get_agent_logger("LeadClassifierAgent") if 'get_agent_logger' in globals() else None
        classifier = LeadClassifierAgent()
        
        classifier_input = {
            "cleaned_leads": cleaned_leads,
            "campaign_id": "test_campaign_123"
        }
        
        start_time = datetime.now()
        if classifier_logger:
            classifier_logger.log_input(classifier_input)
            
        classifier_result = classifier.run(classifier_input)
        end_time = datetime.now()
        
        if classifier_logger:
            classifier_logger.log_output(classifier_result)
            classifier_logger.log_completion("success")
            
        classified_leads = classifier_result.get("classified_leads", [])
        logger.info(f"✅ LeadClassifierAgent a classifié {len(classified_leads)} leads")
        
        test_results.append({
            "agent": "LeadClassifierAgent",
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "status": "success",
            "leads_processed": len(classified_leads)
        })
        
        # 3. Test du CRMExporterAgent (Berinia)
        logger.info("🧪 Test du CRMExporterAgent (Berinia)...")
        exporter_logger = get_agent_logger("CRMExporterAgent") if 'get_agent_logger' in globals() else None
        exporter = CRMExporterAgent()
        
        exporter_input = {
            "classified_leads": classified_leads,
            "campaign_id": "test_campaign_123",
            "pending_leads_count": 5,
            "daily_limit": 20,
            "exported_today": 10
        }
        
        start_time = datetime.now()
        if exporter_logger:
            exporter_logger.log_input(exporter_input)
            
        exporter_result = exporter.run(exporter_input)
        end_time = datetime.now()
        
        if exporter_logger:
            exporter_logger.log_output(exporter_result)
            exporter_logger.log_completion(
                "success" if exporter_result.get("export_status") == "success" else "failure"
            )
            
        export_status = exporter_result.get("export_status")
        export_count = exporter_result.get("leads_count", 0)
        logger.info(f"✅ CRMExporterAgent a exporté {export_count} leads (statut: {export_status})")
        
        test_results.append({
            "agent": "CRMExporterAgent",
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "status": "success",
            "leads_processed": export_count,
            "export_status": export_status,
            "berinia_integration": "active" if berinia_available else "simulation"
        })
        
    except Exception as e:
        logger.error(f"❌ Erreur pendant les tests d'intégration: {str(e)}")
        test_results.append({
            "agent": "IntegrationTest",
            "status": "error",
            "error": str(e)
        })
    
    return test_results

def main():
    """Fonction principale du script"""
    parser = argparse.ArgumentParser(description="Exécute le DecisionBrainAgent de manière isolée")
    parser.add_argument("--operation", default="evaluate_global_strategy",
                        help="Opération à exécuter (evaluate_global_strategy, analyze_campaign, etc.)")
    parser.add_argument("--test-mode", action="store_true",
                        help="Exécuter en mode test (n'affecte pas les données réelles)")
    parser.add_argument("--simulate", action="store_true",
                        help="Simuler les données plutôt que d'utiliser les données réelles")
    parser.add_argument("--verbose", action="store_true",
                        help="Afficher plus de détails sur le processus de décision")
    parser.add_argument("--check-communication", action="store_true",
                        help="Vérifier la communication avec les agents subordonnés")
    parser.add_argument("--integration-tests", action="store_true",
                        help="Exécuter des tests d'intégration avec les autres agents")
    parser.add_argument("--input-file",
                        help="Fichier JSON contenant des données d'entrée supplémentaires")

    args = parser.parse_args()

    # Exécuter l'agent
    result = run_brain_agent(args)

    # Sortir avec le code approprié
    sys.exit(0 if "error" not in result else 1)

if __name__ == "__main__":
    main()
