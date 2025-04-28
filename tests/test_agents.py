"""
Script de test pour vérifier l'initialisation et le fonctionnement de base
des agents BerinIA.
"""

import sys
import os
import traceback

# Assurer que les modules du projet sont dans le path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_agent(agent_class, agent_module, test_input=None):
    """
    Teste l'initialisation et l'exécution de base d'un agent.
    
    Args:
        agent_class: Nom de la classe de l'agent
        agent_module: Chemin d'importation relatif du module
        test_input: Données d'entrée de test (dict)
    
    Returns:
        bool: True si le test réussit, False sinon
    """
    print(f"\n{'='*50}")
    print(f"TEST: {agent_class} depuis {agent_module}")
    print(f"{'='*50}")
    
    if test_input is None:
        test_input = {"test": True}
    
    try:
        # Importation dynamique
        module = __import__(agent_module, fromlist=[agent_class])
        agent_cls = getattr(module, agent_class)
        
        # Instantiation
        print(f"✓ Importation réussie: {agent_class}")
        
        agent = agent_cls()
        print(f"✓ Initialisation réussie: {agent.name}")
        
        # Exécution avec des données minimales
        if hasattr(agent, 'run'):
            print(f"Exécution avec données de test: {test_input}")
            result = agent.run(test_input)
            print(f"✓ Exécution réussie")
            print(f"Résultat: {result}")
            return True
        else:
            print(f"✗ ERREUR: L'agent ne possède pas de méthode 'run'")
            return False
        
    except Exception as e:
        print(f"✗ ERREUR: {str(e)}")
        traceback.print_exc()
        return False


def get_test_input(agent_name):
    """
    Génère des données de test appropriées pour chaque agent
    """
    base_input = {"test": True}
    
    if agent_name == "StrategyAgent":
        return base_input
    elif agent_name == "PlanningAgent":
        return {**base_input, "niche": "Notaires", "priority": "medium"}
    elif agent_name == "AnalyticsAgent":
        return {**base_input, "time_period": "last_30_days"}
    elif agent_name == "PivotAgent":
        return {**base_input, "campaign_data": {"campaign_id": "CAM-TEST"}, "analytics_results": {"metrics": {"conversion_rate": 5.2}}}
    elif agent_name == "MemoryManagerAgent":
        return {**base_input, "operation": "check"}
    elif agent_name == "LeadClassifierAgent":
        return {**base_input, "clean_leads": []}
    elif agent_name == "CRMExporterAgent":
        return {**base_input, "classified_leads": []}
    elif agent_name == "MessengerAgent":
        return {**base_input, "leads_to_contact": []}
    elif agent_name == "CampaignStarterAgent":
        return {**base_input, "validated_niche": {"niche": "Notaires", "priority": "medium"}}
    elif agent_name == "KnowledgeInjectorAgent":
        return {**base_input, "source": "test", "type": "test_data", "data": {"content": "Test content"}}
    elif agent_name == "AgentLoggerAgent":
        return {**base_input, "agent_name": "TestAgent", "input": {"test": True}, "output": {"result": "success"}}
    else:
        return base_input


def run_all_tests():
    """
    Exécute les tests pour tous les agents principaux.
    """
    # Liste des agents à tester (classe, module)
    agents = [
        ("StrategyAgent", "agents.controller.strategy_agent"),
        ("PlanningAgent", "agents.controller.planning_agent"),
        ("AnalyticsAgent", "agents.analytics.analytics_agent"),
        ("PivotAgent", "agents.pivot.pivot_decider"),
        ("MemoryManagerAgent", "agents.controller.memory_manager_agent"),
        ("LeadClassifierAgent", "agents.classifier.lead_classifier_agent"),
        ("CRMExporterAgent", "agents.exporter.crm_exporter_agent"),
        ("MessengerAgent", "agents.messenger.messenger_agent"),
        ("CampaignStarterAgent", "agents.controller.campaign_starter_agent"),
        ("KnowledgeInjectorAgent", "agents.knowledge.knowledge_injector_agent"),
        ("AgentLoggerAgent", "agents.logs.agent_logger_agent"),
    ]
    
    # Compteurs pour le résumé
    success_count = 0
    failure_count = 0
    
    # Exécuter les tests
    for agent_class, agent_module in agents:
        test_input = get_test_input(agent_class)
        success = test_agent(agent_class, agent_module, test_input)
        if success:
            success_count += 1
        else:
            failure_count += 1
    
    # Afficher le résumé
    print(f"\n{'='*50}")
    print(f"RÉSUMÉ DES TESTS")
    print(f"{'='*50}")
    print(f"Agents testés: {len(agents)}")
    print(f"Succès: {success_count}")
    print(f"Échecs: {failure_count}")
    print(f"Taux de réussite: {success_count/len(agents)*100:.1f}%")
    print(f"{'='*50}")


if __name__ == "__main__":
    run_all_tests()
