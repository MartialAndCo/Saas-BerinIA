#!/usr/bin/env python3
"""
Exemple d'intégration des capacités de débogage intelligent avec le Decision Brain Agent.

Ce script montre comment étendre le Decision Brain Agent pour utiliser les agents
de débogage intelligents afin d'améliorer sa capacité à gérer les erreurs.
"""

import os
import sys
import json
import logging
import datetime
import colorama
from colorama import Fore, Style

# Ajouter le chemin racine du projet pour l'importation des modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importer les modules nécessaires
from agents.controller.decision_brain_agent import DecisionBrainAgent
from agents.controller.decision_brain_agent_extensions import extend_decision_brain_agent

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/brain_debugging_demo.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("DebuggingDemo")

# Initialiser colorama pour les logs colorés
colorama.init()

def pretty_print(message, emoji="💡", color=Fore.CYAN):
    """Affiche un message formaté avec emoji et couleur."""
    formatted = f"{color}{emoji} {message}{Style.RESET_ALL}"
    print(formatted)
    logger.info(message)

def main():
    """Fonction principale de démonstration."""
    pretty_print("=== DÉMONSTRATION DE L'INTÉGRATION DU DÉBOGAGE INTELLIGENT ===", 
                emoji="🚀", color=Fore.MAGENTA)
    
    try:
        # Étape 1: Initialiser le Decision Brain Agent standard
        pretty_print("Initialisation du Decision Brain Agent standard...", emoji="🧠")
        brain_agent = DecisionBrainAgent()
        
        # Étape 2: Étendre le Decision Brain Agent avec des capacités de débogage
        pretty_print("Ajout des capacités de débogage intelligent...", emoji="🧩")
        debugging_extension = extend_decision_brain_agent(brain_agent)
        
        # Étape 3: Démontrer la surveillance proactive des services
        pretty_print("Démonstration de la surveillance proactive des services...", emoji="🔍")
        service_status = brain_agent.check_and_repair_services(["berinia-api"])
        
        pretty_print(f"Résultat de la surveillance: {json.dumps(service_status, indent=2)}", 
                    emoji="📊", color=Fore.GREEN)
        
        # Étape 4: Démontrer la gestion d'erreur intelligente
        pretty_print("Démonstration de la gestion d'erreur intelligente...", emoji="🔧")
        
        # Simuler une erreur connue de router non défini
        simulated_error = """
        Traceback (most recent call last):
          File "/root/berinia/backend/app/main.py", line 43, in startup
            from app.api.api import api_router
          File "/root/berinia/backend/app/api/api.py", line 5, in <module>
            from app.api.endpoints import campaigns, niches, leads
          File "/root/berinia/backend/app/api/endpoints/campaigns.py", line 15, in <module>
            @router.get("/")
        NameError: name 'router' is not defined
        """
        
        error_result = brain_agent.handle_exception(
            error_message=simulated_error,
            file_path="/root/berinia/backend/app/api/endpoints/campaigns.py",
            service_name="berinia-api"
        )
        
        pretty_print(f"Résultat de la gestion d'erreur: {json.dumps(error_result, indent=2)}", 
                    emoji="🛠️", color=Fore.YELLOW)
        
        # Étape 5: Démontrer l'enregistrement de feedback
        if "experience_id" in error_result:
            pretty_print("Démonstration de l'enregistrement de feedback...", emoji="💬")
            
            # Simuler un feedback positif de l'humain
            feedback_result = brain_agent._process_debugging_feedback(
                error_result["experience_id"],
                True
            )
            
            pretty_print(f"Résultat du feedback: {json.dumps(feedback_result, indent=2)}", 
                        emoji="👍", color=Fore.GREEN)
        
        # Étape 6: Démontrer l'exécution normale de l'agent
        pretty_print("Démonstration de l'exécution normale du Decision Brain Agent...", emoji="🔄")
        brain_result = brain_agent.run({
            "operation": "evaluate_global_strategy"
        })
        
        pretty_print(f"Exécution normale du cerveau terminée avec succès: {brain_result.get('execution_time', 0):.2f} secondes", 
                    emoji="✅", color=Fore.GREEN)
        
        pretty_print("=== DÉMONSTRATION TERMINÉE AVEC SUCCÈS ===", 
                    emoji="🎉", color=Fore.MAGENTA)
        
    except Exception as e:
        pretty_print(f"Erreur lors de la démonstration: {str(e)}", 
                    emoji="❌", color=Fore.RED)
        logger.exception("Exception non gérée")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
