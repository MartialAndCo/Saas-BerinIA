#!/usr/bin/env python3
"""
Script de test pour l'agent d'analyse.
Exécute directement l'agent AnalyticsAgent avec des données de test.
"""
import os
import sys
import json
import logging
from datetime import datetime

# Configurer le logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("analytics_test")

# S'assurer que les répertoires existent
os.makedirs("logs", exist_ok=True)
os.makedirs("logs/analytics_reports", exist_ok=True)

# Importer l'agent
try:
    # Ajouter le répertoire parent au PYTHONPATH
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from agents.analytics.analytics_agent import AnalyticsAgent
    logger.info("AnalyticsAgent importé avec succès")
except Exception as e:
    logger.error(f"Erreur lors de l'importation de l'agent: {str(e)}")
    sys.exit(1)

def test_campaign_analysis():
    """
    Teste l'analyse de campagne
    """
    logger.info("Test d'analyse de campagne")
    
    # Créer une instance de l'agent
    agent = AnalyticsAgent()
    
    # Données de test
    input_data = {
        "operation": "analyze_campaign",
        "campaign_id": "CAMP123",
        "time_period": "all",
        "output_format": "json",
        "verbose": True
    }
    
    try:
        # Exécuter l'agent
        logger.info("Exécution de l'agent...")
        start_time = datetime.now()
        result = agent.run(input_data)
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # Afficher le résultat
        logger.info(f"Test terminé en {execution_time:.2f} secondes")
        logger.info(f"Statut: {result.get('status', 'UNKNOWN')}")
        
        # Vérifier le résultat
        if result.get("status") == "COMPLETED":
            logger.info("Test réussi ✓")
            # Afficher quelques métriques clés
            if "analysis" in result and "metrics" in result["analysis"]:
                metrics = result["analysis"]["metrics"]
                logger.info(f"Conversion: {metrics.get('conversion_rate', 0) * 100:.1f}%")
                logger.info(f"ROI: {metrics.get('roi', 0) * 100:.1f}%")
                logger.info(f"Coût par lead: {metrics.get('cost_per_lead', 0):.2f}€")
        else:
            logger.error(f"Test échoué: {result.get('error', 'Erreur inconnue')}")
            
        # Sauvegarder le résultat complet
        with open("logs/analytics_test_result.json", "w") as f:
            json.dump(result, f, indent=2)
            
        return result
    except Exception as e:
        logger.error(f"Exception lors du test: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"status": "ERROR", "error": str(e)}

def test_lever_identification():
    """
    Teste l'identification des leviers de performance
    """
    logger.info("Test d'identification des leviers de performance")
    
    # Créer une instance de l'agent
    agent = AnalyticsAgent()
    
    # Données de test
    input_data = {
        "operation": "identify_levers",
        "campaign_id": "CAMP123",
        "output_format": "json",
        "verbose": True
    }
    
    try:
        # Exécuter l'agent
        logger.info("Exécution de l'agent...")
        start_time = datetime.now()
        result = agent.run(input_data)
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # Afficher le résultat
        logger.info(f"Test terminé en {execution_time:.2f} secondes")
        logger.info(f"Statut: {result.get('status', 'UNKNOWN')}")
        
        # Vérifier le résultat
        if result.get("status") == "COMPLETED":
            logger.info("Test réussi ✓")
            # Afficher les principaux leviers
            if "levers" in result:
                for i, lever in enumerate(result["levers"]):
                    logger.info(f"Levier {i+1}: {lever.get('name')} - Impact: {lever.get('impact_score', 0) * 100:.1f}%")
        else:
            logger.error(f"Test échoué: {result.get('error', 'Erreur inconnue')}")
            
        return result
    except Exception as e:
        logger.error(f"Exception lors du test: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"status": "ERROR", "error": str(e)}

def test_performance_prediction():
    """
    Teste la prédiction de performance
    """
    logger.info("Test de prédiction de performance")
    
    # Créer une instance de l'agent
    agent = AnalyticsAgent()
    
    # Données de test
    input_data = {
        "operation": "predict_performance",
        "campaign_id": "CAMP123",
        "output_format": "json",
        "verbose": True
    }
    
    try:
        # Exécuter l'agent
        logger.info("Exécution de l'agent...")
        start_time = datetime.now()
        result = agent.run(input_data)
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # Afficher le résultat
        logger.info(f"Test terminé en {execution_time:.2f} secondes")
        logger.info(f"Statut: {result.get('status', 'UNKNOWN')}")
        
        # Vérifier le résultat
        if result.get("status") == "COMPLETED":
            logger.info("Test réussi ✓")
            # Afficher la confiance et quelques métriques projetées
            if "prediction" in result:
                prediction = result["prediction"]
                logger.info(f"Confiance: {prediction.get('confidence_score', 0) * 100:.1f}%")
                if "projected_metrics" in prediction:
                    metrics = prediction["projected_metrics"]
                    for metric_name, values in metrics.items():
                        if isinstance(values, dict) and "change" in values:
                            change = values["change"]
                            change_str = f"{change:+.2f}" if isinstance(change, (int, float)) else change
                            logger.info(f"{metric_name}: {change_str}")
        else:
            logger.error(f"Test échoué: {result.get('error', 'Erreur inconnue')}")
            
        return result
    except Exception as e:
        logger.error(f"Exception lors du test: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"status": "ERROR", "error": str(e)}

if __name__ == "__main__":
    logger.info("=== Début des tests de l'agent d'analyse ===")
    
    # Exécuter les tests
    analysis_result = test_campaign_analysis()
    logger.info("\n")
    levers_result = test_lever_identification()
    logger.info("\n")
    prediction_result = test_performance_prediction()
    
    # Afficher le résumé
    logger.info("\n=== Résumé des tests ===")
    logger.info(f"Analyse de campagne: {'✓' if analysis_result.get('status') == 'COMPLETED' else '✗'}")
    logger.info(f"Identification des leviers: {'✓' if levers_result.get('status') == 'COMPLETED' else '✗'}")
    logger.info(f"Prédiction de performance: {'✓' if prediction_result.get('status') == 'COMPLETED' else '✗'}")
    
    # Vérifier si tous les tests ont réussi
    all_success = (
        analysis_result.get("status") == "COMPLETED" and
        levers_result.get("status") == "COMPLETED" and
        prediction_result.get("status") == "COMPLETED"
    )
    
    if all_success:
        logger.info("Tous les tests ont réussi!")
        sys.exit(0)
    else:
        logger.error("Certains tests ont échoué.")
        sys.exit(1)
