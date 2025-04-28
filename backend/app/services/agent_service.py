import os
import httpx
import logging
from typing import Dict, Any, Optional

# Configuration
AGENTS_SERVICE_URL = os.getenv("AGENTS_SERVICE_URL", "http://localhost:8555")
TIMEOUT_SECONDS = int(os.getenv("AGENTS_REQUEST_TIMEOUT", "120"))

# Logger
logger = logging.getLogger(__name__)

async def execute_agent(agent_type: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Exécute un agent en envoyant une requête à l'API des agents.
    
    Args:
        agent_type: Le type de l'agent à exécuter (ex: "scraper", "analytics")
        input_data: Les données d'entrée à fournir à l'agent
        
    Returns:
        Dict contenant le résultat de l'exécution
    """
    logger.info(f"Exécution de l'agent de type {agent_type}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{AGENTS_SERVICE_URL}/agents/{agent_type}/execute",
                json=input_data,
                timeout=TIMEOUT_SECONDS
            )
            
            if response.status_code != 200:
                logger.error(f"Erreur lors de l'exécution de l'agent {agent_type}: {response.text}")
                return {
                    "status": "error",
                    "error": f"Service d'agents: {response.status_code} - {response.text}",
                    "execution_time": 0
                }
            
            return response.json()
    
    except httpx.TimeoutException:
        logger.error(f"Timeout lors de l'exécution de l'agent {agent_type}")
        return {
            "status": "error",
            "error": f"Timeout après {TIMEOUT_SECONDS} secondes",
            "execution_time": TIMEOUT_SECONDS
        }
    except Exception as e:
        logger.exception(f"Erreur inattendue lors de l'exécution de l'agent {agent_type}")
        return {
            "status": "error",
            "error": str(e),
            "execution_time": 0
        }

async def get_agent_types() -> list:
    """
    Récupère la liste des types d'agents disponibles
    
    Returns:
        Liste des types d'agents disponibles
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{AGENTS_SERVICE_URL}/agents/types",
                timeout=10.0
            )
            
            if response.status_code != 200:
                logger.error(f"Erreur lors de la récupération des types d'agents: {response.text}")
                return []
            
            return response.json()
    except Exception as e:
        logger.exception("Erreur lors de la récupération des types d'agents")
        return []

async def check_service_status() -> bool:
    """
    Vérifie si le service d'agents est disponible
    
    Returns:
        True si le service est disponible, False sinon
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{AGENTS_SERVICE_URL}/",
                timeout=5.0
            )
            return response.status_code == 200
    except Exception:
        return False
