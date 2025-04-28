#!/usr/bin/env python3
"""
Extensions du Decision Brain Agent pour intégrer les capacités de débogage intelligent.

Ce module ajoute des fonctionnalités de débogage au Decision Brain Agent,
lui permettant de diagnostiquer et corriger automatiquement les problèmes
dans l'infrastructure.
"""

import os
import sys
import json
import logging
import datetime
from typing import Dict, List, Any, Optional, Tuple

# Ajouter le chemin racine du projet pour l'importation des modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Importer les modules nécessaires
from agents.controller.decision_brain_agent import DecisionBrainAgent
from agents.controller.debugging_integration import register_debugging_tools

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/brain_debugging.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("BrainDebugging")

def load_debugging_config() -> Dict[str, Any]:
    """Charge la configuration de débogage."""
    config_path = "config/debugging_config.json"
    
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            logger.warning(f"Fichier de configuration non trouvé: {config_path}. Utilisation des paramètres par défaut.")
            return {
                "confidence_threshold": 0.8,
                "auto_approve": True,
                "service_monitoring": {
                    "interval_minutes": 15,
                    "services": ["berinia-api"]
                },
                "memory_sync": {
                    "interval_hours": 24
                }
            }
    except Exception as e:
        logger.error(f"Erreur lors du chargement de la configuration: {str(e)}")
        return {}


class DebuggingBrainExtension:
    """
    Extension du Decision Brain Agent avec des capacités de débogage intelligent.
    
    Cette classe étend les fonctionnalités du Decision Brain Agent en intégrant
    les outils de débogage intelligent.
    """
    
    def __init__(self, brain_agent: DecisionBrainAgent):
        """Initialise l'extension de débogage."""
        self.brain_agent = brain_agent
        self.debugging_controller = None
        self.config = load_debugging_config()
        
    def initialize(self):
        """Initialise les fonctionnalités de débogage."""
        # Enregistrer les outils de débogage
        self.debugging_controller = register_debugging_tools(self.brain_agent)
        
        # Configurer les tâches planifiées
        self._setup_scheduled_tasks()
        
        # Enrichir le Decision Brain Agent avec des méthodes de débogage
        self._extend_brain_agent()
        
        logger.info("Extension de débogage du Decision Brain Agent initialisée avec succès")
        
    def _setup_scheduled_tasks(self):
        """Configure les tâches planifiées pour le débogage."""
        # Récupérer les paramètres de configuration
        monitoring_config = self.config.get("service_monitoring", {})
        memory_config = self.config.get("memory_sync", {})
        
        # Configurer la surveillance des services
        interval_minutes = monitoring_config.get("interval_minutes", 15)
        services = monitoring_config.get("services", ["berinia-api"])
        
        # Programmer la surveillance périodique des services
        self.brain_agent.schedule_task(
            "monitor_services",
            interval_minutes=interval_minutes,
            args=[services],
            description="Surveillance automatique des services critiques"
        )
        
        # Configurer la synchronisation des mémoires
        interval_hours = memory_config.get("interval_hours", 24)
        
        # Programmer la synchronisation périodique des mémoires
        self.brain_agent.schedule_task(
            "sync_debugging_memories",
            interval_hours=interval_hours,
            description="Synchronisation des mémoires de débogage avec le cerveau principal"
        )
        
        logger.info(f"Tâches de débogage planifiées: surveillance toutes les {interval_minutes} minutes, synchronisation toutes les {interval_hours} heures")
    
    def _extend_brain_agent(self):
        """Étend le Decision Brain Agent avec des méthodes de débogage."""
        # Ajouter des méthodes au Decision Brain Agent
        brain_agent = self.brain_agent
        
        # Méthode pour gérer les exceptions
        def handle_exception(error_message, file_path=None, context=None, service_name=None):
            """Gère une exception détectée dans le système."""
            logger.info(f"Gestion d'une exception: {error_message[:100]}...")
            
            # Utiliser l'outil de débogage pour traiter l'erreur
            result = brain_agent.execute_tool(
                "debug_error",
                error_message=error_message,
                file_path=file_path,
                context=context,
                service_name=service_name
            )
            
            # Enregistrer le résultat dans la mémoire du cerveau
            brain_agent.update_memory({
                "type": "exception_handling",
                "error_message": error_message,
                "file_path": file_path,
                "service_name": service_name,
                "result": result,
                "timestamp": datetime.datetime.now().isoformat()
            })
            
            # Informer l'administrateur si la correction automatique a échoué
            if not result["success"]:
                brain_agent.notify_admin(
                    f"Échec de la correction automatique: {result['message']}",
                    error=error_message,
                    context={
                        "file_path": file_path,
                        "service_name": service_name,
                        "analysis": result.get("analysis", {})
                    }
                )
            
            return result
        
        # Méthode pour traiter les retours d'information sur les corrections
        def process_debugging_feedback(memory_id, success):
            """Traite un retour d'information sur une correction précédente."""
            logger.info(f"Traitement d'un feedback pour la mémoire {memory_id}: {'positif' if success else 'négatif'}")
            
            return brain_agent.execute_tool(
                "provide_debugging_feedback",
                memory_id=memory_id,
                success=success
            )
        
        # Méthode pour vérifier l'état des services et les réparer si nécessaire
        def check_and_repair_services(services=None):
            """Vérifie l'état des services et les répare si nécessaire."""
            if services is None:
                # Utiliser les services configurés par défaut
                services = self.config.get("service_monitoring", {}).get("services", ["berinia-api"])
                
            logger.info(f"Vérification des services: {', '.join(services)}")
            
            return brain_agent.execute_tool(
                "monitor_services",
                services=services
            )
        
        # Ajouter les méthodes au Decision Brain Agent
        brain_agent._handle_exception = handle_exception
        brain_agent._process_debugging_feedback = process_debugging_feedback
        brain_agent._check_and_repair_services = check_and_repair_services
        
        # Rediriger les méthodes originales vers les nouvelles implémentations
        # Cela permet de conserver la compatibilité avec l'API existante
        if hasattr(brain_agent, "handle_exception"):
            brain_agent._original_handle_exception = brain_agent.handle_exception
            brain_agent.handle_exception = handle_exception
            
        if hasattr(brain_agent, "process_feedback"):
            brain_agent._original_process_feedback = brain_agent.process_feedback
            
            def enhanced_process_feedback(feedback_data):
                """Version améliorée de process_feedback qui intègre le débogage."""
                # Si le feedback concerne un débogage, utiliser le traitement spécifique
                if feedback_data.get("type") == "debugging":
                    return process_debugging_feedback(
                        feedback_data.get("memory_id"),
                        feedback_data.get("success", False)
                    )
                # Sinon, utiliser le traitement original
                else:
                    return brain_agent._original_process_feedback(feedback_data)
                    
            brain_agent.process_feedback = enhanced_process_feedback
            
        # Ajouter les nouvelles méthodes
        brain_agent.check_and_repair_services = check_and_repair_services


def extend_decision_brain_agent(brain_agent: DecisionBrainAgent) -> DebuggingBrainExtension:
    """
    Étend le Decision Brain Agent avec des capacités de débogage intelligent.
    
    Cette fonction doit être appelée lors de l'initialisation du système pour
    ajouter les fonctionnalités de débogage au Decision Brain Agent.
    
    Args:
        brain_agent: Instance du Decision Brain Agent à étendre
        
    Returns:
        L'extension de débogage initialisée
    """
    extension = DebuggingBrainExtension(brain_agent)
    extension.initialize()
    return extension


# Exemple d'utilisation
"""
from agents.controller.decision_brain_agent import DecisionBrainAgent
from agents.controller.decision_brain_agent_extensions import extend_decision_brain_agent

# Initialiser le Decision Brain Agent
brain_agent = DecisionBrainAgent()

# Étendre le Decision Brain Agent avec des capacités de débogage
debugging_extension = extend_decision_brain_agent(brain_agent)

# Démarrer le système
brain_agent.start()

# Le Decision Brain Agent peut maintenant détecter et corriger automatiquement les problèmes
# Exemple de détection d'une erreur
brain_agent.handle_exception(
    error_message="NameError: name 'router' is not defined",
    file_path="/root/berinia/backend/app/api/endpoints/campaigns.py",
    service_name="berinia-api"
)

# Exemple de vérification proactive des services
status = brain_agent.check_and_repair_services(["berinia-api"])
"""
