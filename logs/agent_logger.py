"""
Module de journalisation pour les agents.
Fournit des fonctions de journalisation et d'audit des activités des agents.
"""
import os
import json
import datetime
import logging

# Configurer le logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("agents")

# S'assurer que le répertoire de logs existe
os.makedirs("logs", exist_ok=True)

def log_agent(agent_name, input_data, output_data, level="INFO"):
    """
    Enregistre une opération d'agent dans les logs.
    
    Args:
        agent_name: Nom de l'agent
        input_data: Données d'entrée (dict)
        output_data: Données de sortie (dict)
        level: Niveau de journalisation (INFO, WARNING, ERROR)
    """
    # Créer une entrée de journal
    log_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "agent": agent_name,
        "operation": input_data.get("operation", "execute"),
        "input": input_data,
        "output": output_data,
        "status": output_data.get("status", "UNKNOWN")
    }
    
    # Journaliser dans le fichier de logs
    log_to_file(agent_name, log_entry)
    
    # Journaliser dans le logger standard
    if level == "INFO":
        logger.info(f"Agent {agent_name}: {log_entry['operation']} - {log_entry['status']}")
    elif level == "WARNING":
        logger.warning(f"Agent {agent_name}: {log_entry['operation']} - {log_entry['status']}")
    elif level == "ERROR":
        logger.error(f"Agent {agent_name}: {log_entry['operation']} - {log_entry['status']}")
    
    return log_entry

def log_to_file(agent_name, log_entry):
    """
    Enregistre un log dans un fichier JSON spécifique à l'agent.
    
    Args:
        agent_name: Nom de l'agent
        log_entry: Entrée de journal à enregistrer
    """
    try:
        # Créer un timestamp pour le nom du fichier
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        log_filename = f"logs/{agent_name}_{timestamp}.log"
        
        # Analyser le type d'opération pour créer un fichier d'analyse distinct si nécessaire
        operation = log_entry.get("operation", "execute")
        status = log_entry.get("status", "UNKNOWN")
        
        if "analysis" in operation.lower() or "analytics" in agent_name.lower():
            analytics_filename = f"logs/analysis_{operation}_{timestamp}.json"
            
            # Pour les analyses, sauvegarder aussi dans un fichier JSON séparé
            with open(analytics_filename, "w") as f:
                json.dump(log_entry, f, indent=2)
        
        # Enregistrer dans le fichier de logs standard
        with open(log_filename, "w") as f:
            log_text = (
                f"=== {agent_name} LOG ===\n"
                f"Timestamp: {log_entry['timestamp']}\n"
                f"Operation: {operation}\n"
                f"Status: {status}\n\n"
                f"Input: {json.dumps(log_entry['input'], indent=2)}\n\n"
                f"Output: {json.dumps(log_entry['output'], indent=2)}\n"
            )
            f.write(log_text)
        
        return True
    except Exception as e:
        logger.error(f"Erreur lors de l'enregistrement du log pour {agent_name}: {str(e)}")
        return False
