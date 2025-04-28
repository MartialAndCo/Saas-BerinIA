"""
Module de logging amélioré pour les agents BerinIA.
Assure que tous les agents produisent des logs détaillés.
"""

import logging
import os
import json
import datetime
import inspect
import traceback
from pathlib import Path
from typing import Dict, Any, Optional, Union

# Configuration de base du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Créer le dossier logs/agents s'il n'existe pas
os.makedirs("logs/agents", exist_ok=True)
os.makedirs("logs/execution", exist_ok=True)

class EnhancedLogger:
    """
    Logger amélioré pour les agents BerinIA avec enregistrement 
    détaillé des entrées/sorties et des performances.
    """
    
    def __init__(self, agent_name: str):
        """
        Initialise le logger pour un agent spécifique.
        
        Args:
            agent_name: Nom de l'agent
        """
        self.agent_name = agent_name
        self.logger = logging.getLogger(agent_name)
        
        # Configuration du fichier de log
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        log_filename = f"logs/agents/{agent_name}_{timestamp}.log"
        
        # Ajouter un handler pour le fichier
        file_handler = logging.FileHandler(log_filename)
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # Ajouter un handler pour la console
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter('[%(name)s] %(message)s')
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        self.start_time = datetime.datetime.now()
        self.logger.info(f"🚀 {agent_name} démarré")
        
    def log_input(self, input_data: Any):
        """
        Enregistre les données d'entrée de l'agent.
        
        Args:
            input_data: Données d'entrée de l'agent
        """
        # Nettoyer et formater les données pour le log
        if isinstance(input_data, dict):
            # Copier le dictionnaire pour ne pas modifier l'original
            clean_data = input_data.copy()
            # Supprimer ou tronquer les grandes valeurs
            for key, value in clean_data.items():
                if isinstance(value, str) and len(value) > 500:
                    clean_data[key] = f"{value[:500]}... [tronqué, longueur totale: {len(value)}]"
                elif isinstance(value, list) and len(value) > 20:
                    clean_data[key] = f"{value[:20]}... [tronqué, {len(value)} éléments]"
            log_data = clean_data
        else:
            log_data = str(input_data)
            
        try:
            self.logger.info(f"📥 Données d'entrée: {json.dumps(log_data, ensure_ascii=False)}")
        except (TypeError, ValueError):
            self.logger.info(f"📥 Données d'entrée: {str(log_data)}")
    
    def log_processing(self, message: str):
        """
        Enregistre une étape de traitement.
        
        Args:
            message: Message décrivant l'étape
        """
        self.logger.info(f"⚙️ {message}")
    
    def log_output(self, output_data: Any, execution_time: Optional[float] = None):
        """
        Enregistre les données de sortie de l'agent.
        
        Args:
            output_data: Données de sortie de l'agent
            execution_time: Temps d'exécution en ms (optionnel)
        """
        # Calculer le temps d'exécution si non fourni
        if execution_time is None:
            end_time = datetime.datetime.now()
            execution_time = (end_time - self.start_time).total_seconds() * 1000
            
        # Formater et enregistrer les données de sortie
        try:
            if isinstance(output_data, dict):
                # Nettoyer les grandes valeurs
                clean_output = output_data.copy()
                for key, value in clean_output.items():
                    if isinstance(value, str) and len(value) > 500:
                        clean_output[key] = f"{value[:500]}... [tronqué, longueur totale: {len(value)}]"
                    elif isinstance(value, list) and len(value) > 20:
                        clean_output[key] = f"{value[:20]}... [tronqué, {len(value)} éléments]"
                
                self.logger.info(f"📤 Résultat: {json.dumps(clean_output, ensure_ascii=False)}")
            else:
                self.logger.info(f"📤 Résultat: {str(output_data)}")
        except (TypeError, ValueError) as e:
            self.logger.info(f"📤 Résultat: [Objet non sérialisable: {type(output_data)}]")
            
        # Enregistrer le temps d'exécution
        self.logger.info(f"⏱️ Temps d'exécution: {execution_time:.2f} ms")
    
    def log_error(self, error: Union[str, Exception], context: Optional[Dict[str, Any]] = None):
        """
        Enregistre une erreur avec contexte.
        
        Args:
            error: L'erreur ou message d'erreur
            context: Contexte additionnel (optionnel)
        """
        if isinstance(error, Exception):
            error_msg = f"{type(error).__name__}: {str(error)}"
            stack_trace = traceback.format_exc()
        else:
            error_msg = error
            stack_trace = "".join(traceback.format_stack()[:-1])
            
        self.logger.error(f"❌ ERREUR: {error_msg}")
        self.logger.debug(f"Stack trace:\n{stack_trace}")
        
        if context:
            self.logger.error(f"Contexte de l'erreur: {json.dumps(context, ensure_ascii=False, default=str)}")
    
    def log_completion(self, status: str = "success"):
        """
        Enregistre la fin de l'exécution de l'agent.
        
        Args:
            status: Statut de fin ('success', 'failure', etc.)
        """
        end_time = datetime.datetime.now()
        execution_time = (end_time - self.start_time).total_seconds() * 1000
        
        if status == "success":
            self.logger.info(f"✅ {self.agent_name} terminé avec succès en {execution_time:.2f} ms")
        else:
            self.logger.warning(f"⚠️ {self.agent_name} terminé avec statut '{status}' en {execution_time:.2f} ms")

def log_system_execution(agent_flow: list, output_data: Any, campaign_id: Optional[str] = None):
    """
    Enregistre l'exécution complète du système avec le flux d'agents
    et les données de sortie.
    
    Args:
        agent_flow: Liste des agents exécutés dans l'ordre
        output_data: Données de sortie finale
        campaign_id: ID de la campagne (optionnel)
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"logs/execution/system_execution_{timestamp}.json"
    
    # Créer le rapport d'exécution
    execution_report = {
        "timestamp": datetime.datetime.now().isoformat(),
        "campaign_id": campaign_id,
        "agent_flow": agent_flow,
        "result": output_data,
        "execution_time": {
            "start": agent_flow[0].get("start_time"),
            "end": datetime.datetime.now().isoformat(),
        }
    }
    
    # Enregistrer le rapport au format JSON
    with open(filename, 'w') as f:
        json.dump(execution_report, f, ensure_ascii=False, indent=2, default=str)
    
    return filename

# Fonction utilitaire pour obtenir facilement un logger
def get_agent_logger(agent_name: str) -> EnhancedLogger:
    """
    Fonction utilitaire pour obtenir un logger amélioré pour un agent.
    
    Args:
        agent_name: Nom de l'agent
        
    Returns:
        EnhancedLogger: Logger amélioré pour l'agent
    """
    return EnhancedLogger(agent_name)

# Exemple d'utilisation
if __name__ == "__main__":
    # Exemple d'utilisation du logger
    logger = get_agent_logger("TestAgent")
    
    # Test des différentes fonctions de logging
    logger.log_input({"test_param": "valeur", "big_data": "x" * 1000})
    logger.log_processing("Analyse des données en cours...")
    
    try:
        # Simuler une erreur
        result = 1 / 0
    except Exception as e:
        logger.log_error(e, {"étape": "division", "valeurs": [1, 0]})
    
    logger.log_output({"résultat": "OK", "données": [1, 2, 3, 4, 5]})
    logger.log_completion()
    
    # Test du log système
    agent_flow = [
        {"agent": "TestAgent", "start_time": "2025-04-27T10:00:00"},
        {"agent": "AnalyticsAgent", "start_time": "2025-04-27T10:01:00"}
    ]
    log_file = log_system_execution(agent_flow, {"status": "completed"})
    print(f"Log système enregistré dans {log_file}")
