from datetime import datetime
import logging
from abc import ABC, abstractmethod

class BaseAgent(ABC):
    """
    Classe de base pour tous les agents du système.
    Implémente les fonctionnalités communes à tous les agents, notamment
    le logging, l'évaluation et le feedback.
    """
    def __init__(self, agent_id, db_session):
        self.agent_id = agent_id
        self.db = db_session
        self.agent_model = self.db.query(AgentModel).filter(AgentModel.id == agent_id).first()
        self.logger = self.setup_logger()
    
    def setup_logger(self):
        """
        Configure le logger pour l'agent.
        """
        logger = logging.getLogger(f"{self.__class__.__name__}")
        logger.setLevel(logging.INFO)
        
        # Create handlers if not already configured
        if not logger.handlers:
            # File handler
            file_handler = logging.FileHandler(
                f"logs/{self.__class__.__name__}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
            )
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
            
        return logger
    
    @abstractmethod
    def run(self, input_data):
        """
        Méthode principale à implémenter par chaque agent.
        
        Args:
            input_data: Les données d'entrée pour l'agent
            
        Returns:
            dict: Les résultats de l'exécution de l'agent
        """
        pass
        
    def log_execution(self, operation, input_data, output_data, status, execution_time):
        """
        Enregistre l'exécution de l'agent dans la base de données.
        
        Args:
            operation (str): Type d'opération effectuée
            input_data (dict): Données d'entrée
            output_data (dict): Données de sortie
            status (str): Statut de l'exécution (success, error, etc.)
            execution_time (float): Temps d'exécution en secondes
            
        Returns:
            int: ID de l'entrée de log créée
        """
        # Enregistrer dans la base de données
        log_entry = AgentLog(
            agent_id=self.agent_id,
            operation=operation,
            input_data=input_data,
            output_data=output_data,
            status=status,
            execution_time=execution_time
        )
        self.db.add(log_entry)
        self.db.commit()
        
        # Auto-évaluation immédiate si configurée
        if self.agent_model.configuration.get("auto_evaluate", False):
            self.auto_evaluate_log(log_entry.id)
            
        return log_entry.id
        
    def auto_evaluate_log(self, log_id):
        """
        Implémentation de base de l'auto-évaluation.
        Cette méthode pourra être enrichie par le SelfEvaluationAgent.
        
        Args:
            log_id (int): ID de l'entrée de log à évaluer
        """
        # Implémentation basique qui sera enrichie par SelfEvaluationAgent
        self.logger.info(f"Auto-évaluation requise pour le log {log_id}")
        # L'implémentation complète sera faite dans SelfEvaluationAgent
