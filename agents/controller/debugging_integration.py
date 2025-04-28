#!/usr/bin/env python3
"""
Module d'intégration des agents de débogage avec le Decision Brain Agent.

Ce module permet au Decision Brain Agent (agent principal contrôleur) 
d'utiliser les agents de débogage intelligents pour résoudre
automatiquement les problèmes dans le système.
"""

import os
import sys
import json
import logging
import datetime
from typing import Dict, List, Any, Optional, Tuple

# Ajouter le chemin racine du projet pour l'importation des modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Importer les agents de débogage
try:
    from scripts.smart_debugger_agent import SmartDebugger
    from scripts.auto_diagnose import FastAPIDiagnostic
    from scripts.fix_berinia_intelligent import BeriniaIntelligentFixer
except ImportError:
    logging.warning("Les agents de débogage n'ont pas été trouvés. Installation des dépendances requises...")
    
# Importer les composants du contrôleur
from agents.controller.decision_brain_agent import DecisionBrainAgent
from agents.base.base import AgentResponse

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/debugging_controller.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("DebuggingController")

class DebuggingController:
    """
    Contrôleur pour l'intégration des agents de débogage avec le Decision Brain Agent.
    
    Cette classe agit comme une interface entre le Decision Brain Agent et les
    agents de débogage intelligents, permettant au contrôleur principal de déléguer
    des tâches de diagnostic et de correction aux agents spécialisés.
    """
    
    def __init__(self, brain_agent: Optional[DecisionBrainAgent] = None):
        """Initialise le contrôleur de débogage."""
        self.brain_agent = brain_agent
        self.smart_debugger = None
        self.fastapi_diagnostic = None
        self.berinia_fixer = None
        
    def initialize_agents(self):
        """Initialise les agents de débogage à la demande."""
        try:
            if self.smart_debugger is None:
                self.smart_debugger = SmartDebugger()
                logger.info("Agent SmartDebugger initialisé avec succès")
                
            if self.fastapi_diagnostic is None:
                self.fastapi_diagnostic = FastAPIDiagnostic(project_path="/root/berinia/backend")
                logger.info("Agent FastAPIDiagnostic initialisé avec succès")
                
            if self.berinia_fixer is None:
                self.berinia_fixer = BeriniaIntelligentFixer()
                logger.info("Agent BeriniaIntelligentFixer initialisé avec succès")
                
            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation des agents de débogage: {str(e)}")
            return False
    
    def handle_error(self, error_message: str, file_path: Optional[str] = None, 
                    context: Optional[str] = None, service_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Gère une erreur détectée par le Decision Brain Agent.
        
        Args:
            error_message: Message d'erreur à analyser
            file_path: Chemin du fichier contenant l'erreur
            context: Contexte supplémentaire (stacktrace, logs, etc.)
            service_name: Nom du service ayant rencontré l'erreur
            
        Returns:
            Un dictionnaire contenant le résultat de l'analyse et de la correction
        """
        # Initialiser les agents si nécessaire
        if not self.initialize_agents():
            return {
                "success": False,
                "message": "Impossible d'initialiser les agents de débogage",
                "timestamp": datetime.datetime.now().isoformat()
            }
        
        # Choisir l'agent approprié en fonction du contexte
        if service_name == "berinia-api" or "berinia" in str(file_path).lower():
            return self._handle_berinia_error(error_message, file_path, context)
        elif "fastapi" in error_message.lower() or "uvicorn" in error_message.lower():
            return self._handle_fastapi_error(error_message, file_path, context)
        else:
            return self._handle_generic_error(error_message, file_path, context)
    
    def _handle_berinia_error(self, error_message: str, file_path: Optional[str], 
                             context: Optional[str]) -> Dict[str, Any]:
        """Gère une erreur spécifique à Berinia."""
        try:
            # Diagnostic initial
            logger.info(f"Diagnostic de l'erreur Berinia: {error_message[:100]}...")
            issues = self.berinia_fixer.diagnose()
            
            if not issues:
                logger.info("Aucun problème détecté dans Berinia")
                return {
                    "success": False,
                    "message": "Aucun problème détecté dans Berinia. Analyse manuelle requise.",
                    "timestamp": datetime.datetime.now().isoformat()
                }
            
            # Appliquer les corrections automatiquement
            logger.info(f"Application des corrections pour {len(issues)} problèmes dans Berinia")
            fixes = self.berinia_fixer.fix_issues(auto_approve=True)
            
            if fixes:
                # Redémarrer le service si nécessaire
                restart_success = self.berinia_fixer.restart_service()
                
                # Générer un rapport
                report = self.berinia_fixer.generate_report()
                
                # Informer le Decision Brain Agent
                if self.brain_agent:
                    self.brain_agent.update_memory({
                        "type": "debugging_action",
                        "service": "berinia-api",
                        "action": "auto_fix",
                        "issues_fixed": len(fixes),
                        "restart_success": restart_success,
                        "timestamp": datetime.datetime.now().isoformat()
                    })
                
                return {
                    "success": True,
                    "message": f"Corrections appliquées avec succès pour {len(fixes)} problèmes dans Berinia",
                    "restart_success": restart_success,
                    "report": report,
                    "timestamp": datetime.datetime.now().isoformat()
                }
            else:
                logger.warning("Aucune correction n'a pu être appliquée pour Berinia")
                return {
                    "success": False,
                    "message": "Aucune correction n'a pu être appliquée. Intervention manuelle requise.",
                    "issues": issues,
                    "timestamp": datetime.datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Erreur lors du traitement de l'erreur Berinia: {str(e)}")
            return {
                "success": False,
                "message": f"Erreur lors du traitement: {str(e)}",
                "timestamp": datetime.datetime.now().isoformat()
            }
    
    def _handle_fastapi_error(self, error_message: str, file_path: Optional[str], 
                             context: Optional[str]) -> Dict[str, Any]:
        """Gère une erreur FastAPI générique."""
        try:
            # Définir le projet à analyser
            project_path = "/root/berinia/backend"
            if file_path:
                # Déterminer le projet à partir du chemin du fichier
                if "/berinia/" in file_path:
                    project_path = "/root/berinia/backend"
                
            # Instancier le diagnostic
            diagnostic = FastAPIDiagnostic(project_path=project_path)
            
            # Exécuter l'analyse
            logger.info(f"Analyse du projet FastAPI: {project_path}")
            issues = diagnostic.analyze_all()
            
            if not issues:
                logger.info("Aucun problème détecté dans le projet FastAPI")
                return {
                    "success": False,
                    "message": "Aucun problème détecté dans le projet FastAPI. Analyse manuelle requise.",
                    "timestamp": datetime.datetime.now().isoformat()
                }
            
            # Appliquer les corrections automatiquement
            logger.info(f"Application des corrections pour {len(issues)} problèmes FastAPI")
            fixes = diagnostic.fix_issues(auto_fix=True)
            
            # Générer un rapport
            report = diagnostic.generate_report()
            
            # Informer le Decision Brain Agent
            if self.brain_agent and fixes:
                self.brain_agent.update_memory({
                    "type": "debugging_action",
                    "project": project_path,
                    "action": "auto_fix",
                    "issues_fixed": len(fixes),
                    "timestamp": datetime.datetime.now().isoformat()
                })
            
            return {
                "success": len(fixes) > 0,
                "message": f"Corrections appliquées avec succès pour {len(fixes)} problèmes FastAPI" if fixes else "Aucune correction appliquée",
                "report": report,
                "timestamp": datetime.datetime.now().isoformat()
            }
                
        except Exception as e:
            logger.error(f"Erreur lors du traitement de l'erreur FastAPI: {str(e)}")
            return {
                "success": False,
                "message": f"Erreur lors du traitement: {str(e)}",
                "timestamp": datetime.datetime.now().isoformat()
            }
    
    def _handle_generic_error(self, error_message: str, file_path: Optional[str], 
                             context: Optional[str]) -> Dict[str, Any]:
        """Gère une erreur générique avec l'agent SmartDebugger."""
        try:
            # Analyser l'erreur
            logger.info(f"Analyse de l'erreur générique: {error_message[:100]}...")
            analysis = self.smart_debugger.analyze_error(
                error_message=error_message,
                file_path=file_path,
                code_context=context
            )
            
            # Si l'agent a une solution avec une confiance élevée, l'appliquer
            if analysis.get("confidence", 0) > 0.8 and "experience_id" in analysis:
                error_type = self._determine_error_type(analysis)
                if error_type and file_path:
                    # Appliquer la correction
                    logger.info(f"Application de la correction {error_type} pour {file_path}")
                    result = self.smart_debugger.apply_fix(error_type, file_path)
                    
                    # Enregistrer le résultat dans la mémoire du Decision Brain Agent
                    if self.brain_agent and result["success"]:
                        self.brain_agent.update_memory({
                            "type": "debugging_action",
                            "file": file_path,
                            "error_type": error_type,
                            "action": "auto_fix",
                            "message": result["message"],
                            "experience_id": analysis["experience_id"],
                            "timestamp": datetime.datetime.now().isoformat()
                        })
                    
                    return {
                        "success": result["success"],
                        "message": result["message"],
                        "error_type": error_type,
                        "confidence": analysis["confidence"],
                        "experience_id": analysis["experience_id"],
                        "timestamp": datetime.datetime.now().isoformat()
                    }
            
            # Sinon, signaler qu'une intervention manuelle est nécessaire
            return {
                "success": False,
                "message": "Confiance insuffisante pour une correction automatique. Intervention humaine requise.",
                "analysis": analysis,
                "timestamp": datetime.datetime.now().isoformat()
            }
                
        except Exception as e:
            logger.error(f"Erreur lors du traitement de l'erreur générique: {str(e)}")
            return {
                "success": False,
                "message": f"Erreur lors du traitement: {str(e)}",
                "timestamp": datetime.datetime.now().isoformat()
            }
    
    def _determine_error_type(self, analysis: Dict[str, Any]) -> Optional[str]:
        """Détermine le type d'erreur à partir de l'analyse."""
        if not analysis or "recommended_solution" not in analysis:
            return None
            
        solution = analysis["recommended_solution"]
        error_message = analysis.get("error", "")
        
        if "indentation" in solution.lower() or "indentation" in error_message.lower():
            return "indentation"
        elif "router" in solution.lower() and "not defined" in solution.lower():
            return "router_not_defined"
        elif "router" in solution.lower() and "prefix" in solution.lower():
            return "router_prefix_duplicate"
        elif "sa_instance_state" in solution.lower() or "_sa_instance_state" in error_message.lower():
            return "sa_instance_state"
        else:
            return None
    
    def monitor_services(self, services: List[str] = None) -> Dict[str, Any]:
        """
        Surveille proactivement les services spécifiés.
        
        Args:
            services: Liste des services à surveiller (par défaut: ["berinia-api"])
            
        Returns:
            Un rapport sur l'état des services
        """
        if services is None:
            services = ["berinia-api"]
            
        results = {}
        
        for service in services:
            if service == "berinia-api":
                # Initialiser le fixer si nécessaire
                if not self.initialize_agents() or self.berinia_fixer is None:
                    results[service] = {
                        "success": False,
                        "message": "Impossible d'initialiser l'agent de diagnostic Berinia",
                        "timestamp": datetime.datetime.now().isoformat()
                    }
                    continue
                
                # Vérifier l'état du service
                status = self.berinia_fixer.check_service_status()
                
                if not status["running"]:
                    # Analyser le problème
                    issues = self.berinia_fixer.analyze_service_issues()
                    
                    if issues:
                        # Tenter une correction automatique
                        fixes = self.berinia_fixer.fix_issues(auto_approve=True)
                        
                        # Redémarrer le service
                        restart_success = False
                        if fixes:
                            restart_success = self.berinia_fixer.restart_service()
                            
                            # Informer le Decision Brain Agent
                            if self.brain_agent:
                                self.brain_agent.update_memory({
                                    "type": "service_recovery",
                                    "service": service,
                                    "issues_fixed": len(fixes),
                                    "restart_success": restart_success,
                                    "timestamp": datetime.datetime.now().isoformat()
                                })
                        
                        results[service] = {
                            "success": restart_success,
                            "running": restart_success,
                            "issues_detected": len(issues),
                            "fixes_applied": len(fixes),
                            "message": f"Service restauré avec {len(fixes)} corrections" if restart_success else "Échec de la restauration du service",
                            "timestamp": datetime.datetime.now().isoformat()
                        }
                    else:
                        results[service] = {
                            "success": False,
                            "running": False,
                            "issues_detected": 0,
                            "message": "Service arrêté, aucun problème détectable automatiquement",
                            "timestamp": datetime.datetime.now().isoformat()
                        }
                else:
                    results[service] = {
                        "success": True,
                        "running": True,
                        "message": "Service en cours d'exécution",
                        "timestamp": datetime.datetime.now().isoformat()
                    }
        
        return results
    
    def provide_feedback(self, memory_id: str, success: bool) -> bool:
        """
        Fournit un retour d'information sur une correction précédente.
        
        Args:
            memory_id: ID de la mémoire de débogage
            success: Si la correction a été réussie
            
        Returns:
            True si le feedback a été enregistré avec succès
        """
        try:
            if not self.initialize_agents() or self.smart_debugger is None:
                logger.error("Impossible d'initialiser l'agent SmartDebugger pour le feedback")
                return False
                
            # Enregistrer le feedback dans la mémoire de l'agent
            feedback_result = self.smart_debugger.save_feedback(
                memory_id, 
                "positive" if success else "negative"
            )
            
            # Enregistrer également ce feedback dans la mémoire du Decision Brain Agent
            if self.brain_agent and feedback_result:
                self.brain_agent.update_memory({
                    "type": "debugging_feedback",
                    "memory_id": memory_id,
                    "feedback": "positive" if success else "negative",
                    "timestamp": datetime.datetime.now().isoformat()
                })
                
            return feedback_result
            
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement du feedback: {str(e)}")
            return False
    
    def sync_memories(self) -> bool:
        """
        Synchronise les mémoires des agents de débogage avec le Decision Brain Agent.
        
        Returns:
            True si la synchronisation a réussi
        """
        if not self.brain_agent:
            logger.warning("Pas de Decision Brain Agent connecté pour la synchronisation des mémoires")
            return False
            
        try:
            if not self.initialize_agents() or self.smart_debugger is None:
                logger.error("Impossible d'initialiser l'agent SmartDebugger pour la synchronisation")
                return False
                
            # Récupérer les expériences de débogage
            debugging_memories = self.smart_debugger.memory.memories
            
            # Transférer les expériences réussies vers la mémoire du Decision Brain Agent
            sync_count = 0
            for memory in debugging_memories:
                if memory.get("feedback") == "positive":
                    self.brain_agent.update_memory({
                        "type": "debugging_experience",
                        "source": "smart_debugger",
                        "memory_id": memory["id"],
                        "problem": memory["problem"],
                        "solution": memory["solution"],
                        "outcome": memory["outcome"],
                        "files_modified": memory["files_modified"],
                        "timestamp": memory["timestamp"]
                    })
                    sync_count += 1
            
            logger.info(f"Synchronisation réussie de {sync_count} mémoires de débogage")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la synchronisation des mémoires: {str(e)}")
            return False


# Interface pour le Decision Brain Agent
def register_debugging_tools(brain_agent: DecisionBrainAgent) -> DebuggingController:
    """
    Enregistre les outils de débogage auprès du Decision Brain Agent.
    
    Cette fonction doit être appelée lors de l'initialisation du Decision Brain Agent
    pour lui donner accès aux capacités de débogage.
    
    Args:
        brain_agent: Instance du Decision Brain Agent
        
    Returns:
        Le contrôleur de débogage initialisé
    """
    controller = DebuggingController(brain_agent)
    
    # Enregistrer les fonctions de débogage comme outils du Brain
    brain_agent.register_tool(
        "debug_error",
        controller.handle_error,
        "Analyse et corrige automatiquement une erreur détectée dans le système"
    )
    
    brain_agent.register_tool(
        "monitor_services",
        controller.monitor_services,
        "Surveille proactivement les services spécifiés et tente de les restaurer si nécessaire"
    )
    
    brain_agent.register_tool(
        "provide_debugging_feedback",
        controller.provide_feedback,
        "Fournit un retour d'information sur une correction précédente pour améliorer les futurs déboguages"
    )
    
    brain_agent.register_tool(
        "sync_debugging_memories",
        controller.sync_memories,
        "Synchronise les mémoires des agents de débogage avec le Decision Brain Agent"
    )
    
    return controller


# Exemple d'utilisation dans le Decision Brain Agent
"""
from agents.controller.debugging_integration import register_debugging_tools

class DecisionBrainAgent:
    # ...autres méthodes...
    
    def initialize(self):
        # Enregistrer les outils de débogage
        self.debugging_controller = register_debugging_tools(self)
        
        # Programmer la surveillance périodique
        self.schedule_task(
            "monitor_services",
            interval_minutes=15,
            args=[["berinia-api"]]
        )
        
        # Programmer la synchronisation des mémoires
        self.schedule_task(
            "sync_debugging_memories",
            interval_hours=24
        )
    
    def handle_exception(self, error_message, file_path=None, context=None):
        # Utiliser les outils de débogage pour gérer l'exception
        result = self.execute_tool(
            "debug_error",
            error_message=error_message,
            file_path=file_path,
            context=context
        )
        
        if not result["success"]:
            # Informer l'administrateur si la correction automatique a échoué
            self.notify_admin(
                f"Échec de la correction automatique: {result['message']}",
                error=error_message
            )
"""
