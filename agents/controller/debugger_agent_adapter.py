#!/usr/bin/env python3
"""
Adaptateur pour intégrer les agents de débogage intelligents au DebuggerAgent existant.

Ce module permet au DebuggerAgent existant d'utiliser les nouveaux agents de débogage
intelligents, tout en préservant l'interface existante pour la compatibilité.
"""

import os
import sys
import json
import logging
import datetime
from typing import Dict, List, Any, Optional, Tuple

# Ajouter le chemin racine du projet pour l'importation des modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Importer les agents de débogage intelligents
try:
    from scripts.smart_debugger_agent import SmartDebugger
    from scripts.auto_diagnose import FastAPIDiagnostic
    from scripts.fix_berinia_intelligent import BeriniaIntelligentFixer
except ImportError:
    logging.warning("Les agents de débogage intelligents n'ont pas été trouvés. L'adaptateur fonctionnera en mode limité.")

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/debugger_adapter.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("DebuggerAdapter")

class IntelligentDebugAdapter:
    """
    Adaptateur qui permet au DebuggerAgent existant d'utiliser les agents de débogage intelligents.
    
    Cette classe sert d'interface entre l'ancien DebuggerAgent et les nouveaux agents
    de débogage, assurant la compatibilité tout en tirant parti des nouvelles capacités.
    """
    
    def __init__(self):
        """Initialise l'adaptateur de débogage."""
        self.smart_debugger = None
        self.fastapi_diagnostic = None
        self.berinia_fixer = None
        self.initialized = self._initialize_agents()
        
    def _initialize_agents(self) -> bool:
        """Initialise les agents de débogage intelligents à la demande."""
        try:
            self.smart_debugger = SmartDebugger()
            logger.info("Agent SmartDebugger initialisé avec succès")
            
            self.fastapi_diagnostic = FastAPIDiagnostic(project_path="/root/berinia/backend")
            logger.info("Agent FastAPIDiagnostic initialisé avec succès")
            
            self.berinia_fixer = BeriniaIntelligentFixer()
            logger.info("Agent BeriniaIntelligentFixer initialisé avec succès")
            
            return True
        except (NameError, ImportError) as e:
            logger.warning(f"Impossible d'initialiser les agents de débogage intelligents: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation des agents de débogage: {str(e)}")
            return False
    
    def analyze_error(self, failed_agent: str, error_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyse une erreur détectée par le DebuggerAgent.
        
        Args:
            failed_agent: Nom de l'agent qui a échoué
            error_message: Message d'erreur
            context: Contexte supplémentaire
            
        Returns:
            Un dictionnaire contenant le résultat de l'analyse
        """
        if not self.initialized:
            logger.warning("Les agents de débogage intelligents ne sont pas disponibles. Analyse limitée.")
            # Retourner un format compatible avec DebuggerAgent
            return {
                "status": "ANALYSIS_COMPLETE",
                "diagnostic": {
                    "summary": "Analyse limitée (agents intelligents non disponibles)",
                    "error_type": "unknown",
                    "severity": "unknown",
                    "details": f"Erreur dans l'agent {failed_agent}: {error_message}"
                },
                "resolution_action": "NOTIFY_ADMIN",
                "resolution_details": "Les agents de débogage intelligents ne sont pas disponibles.",
                "requires_human": True,
                "timestamp": datetime.datetime.now().isoformat()
            }
        
        # Déterminer le type d'erreur et l'agent à utiliser
        try:
            # Extraire le chemin du fichier du message d'erreur s'il est présent
            file_path = None
            if "File \"" in error_message:
                for line in error_message.split("\n"):
                    if "File \"" in line:
                        file_path_match = line.split("File \"")[1].split("\"")[0]
                        file_path = file_path_match
                        break
            
            # Déterminer le service concerné
            service_name = None
            if "berinia" in error_message.lower() or (file_path and "berinia" in file_path.lower()):
                service_name = "berinia-api"
            
            # Enregistrer l'extraction des informations
            logger.info(f"Informations extraites de l'erreur: fichier={file_path}, service={service_name}")
            
            # Cas 1: Erreur dans Berinia API
            if service_name == "berinia-api":
                return self._analyze_berinia_error(error_message, file_path, context)
            
            # Cas 2: Erreur dans FastAPI générique
            elif "fastapi" in error_message.lower() or "uvicorn" in error_message.lower():
                return self._analyze_fastapi_error(error_message, file_path, context)
            
            # Cas 3: Erreur générique
            else:
                return self._analyze_generic_error(error_message, file_path, context)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse: {str(e)}")
            return {
                "status": "ERROR",
                "diagnostic": {
                    "summary": f"Erreur lors de l'analyse: {str(e)}",
                    "error_type": "adapter_error",
                    "severity": "high",
                    "details": f"Exception dans l'adaptateur: {str(e)}"
                },
                "resolution_action": "NOTIFY_ADMIN",
                "requires_human": True,
                "timestamp": datetime.datetime.now().isoformat()
            }
    
    def _analyze_berinia_error(self, error_message: str, file_path: Optional[str], context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse une erreur spécifique à Berinia."""
        # Utiliser BeriniaIntelligentFixer
        try:
            # Lancer un diagnostic Berinia
            issues = self.berinia_fixer.diagnose()
            
            if not issues:
                return {
                    "status": "ANALYSIS_COMPLETE",
                    "diagnostic": {
                        "summary": "Aucun problème détecté dans Berinia malgré l'erreur signalée",
                        "error_type": "unknown",
                        "severity": "medium",
                        "details": error_message
                    },
                    "resolution_action": "NOTIFY_ADMIN",
                    "resolution_details": "L'agent Berinia n'a pas détecté de problème. Vérification manuelle requise.",
                    "requires_human": True,
                    "timestamp": datetime.datetime.now().isoformat()
                }
            
            # Déterminer si nous pouvons corriger automatiquement
            can_auto_fix = any(issue["error_type"] in ["indentation", "sa_instance_state", "router_not_defined", "router_prefix_duplicate"] for issue in issues)
            
            if can_auto_fix:
                return {
                    "status": "ANALYSIS_COMPLETE",
                    "diagnostic": {
                        "summary": f"Problème(s) détecté(s) dans Berinia: {len(issues)} issues",
                        "error_type": issues[0]["error_type"],
                        "severity": "high",
                        "details": json.dumps(issues, indent=2)
                    },
                    "resolution_action": "AUTO_RESOLVE",
                    "resolution_method": "berinia_fixer",
                    "resolution_details": "L'agent intelligent de Berinia peut réparer ce problème automatiquement",
                    "requires_human": False,
                    "auto_resolution_ready": True,
                    "timestamp": datetime.datetime.now().isoformat()
                }
            else:
                return {
                    "status": "ANALYSIS_COMPLETE",
                    "diagnostic": {
                        "summary": f"Problème(s) complexe(s) détecté(s) dans Berinia: {len(issues)} issues",
                        "error_type": "complex",
                        "severity": "high",
                        "details": json.dumps(issues, indent=2)
                    },
                    "resolution_action": "SUGGEST_FIX",
                    "resolution_details": "Problèmes détectés nécessitant une validation humaine",
                    "requires_human": True,
                    "timestamp": datetime.datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse Berinia: {str(e)}")
            return {
                "status": "ERROR",
                "diagnostic": {
                    "summary": f"Erreur lors de l'analyse Berinia: {str(e)}",
                    "error_type": "analyzer_error",
                    "severity": "high",
                    "details": f"Exception dans l'analyseur Berinia: {str(e)}"
                },
                "resolution_action": "NOTIFY_ADMIN",
                "requires_human": True,
                "timestamp": datetime.datetime.now().isoformat()
            }
    
    def _analyze_fastapi_error(self, error_message: str, file_path: Optional[str], context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse une erreur FastAPI générique."""
        # Utiliser FastAPIDiagnostic
        try:
            # Déterminer le projet à analyser
            project_path = "/root/berinia/backend"
            if file_path:
                # Déterminer le projet à partir du chemin du fichier
                if "/berinia/" in file_path:
                    project_path = "/root/berinia/backend"
            
            # Exécuter l'analyse FastAPI
            issues = self.fastapi_diagnostic.analyze_all()
            
            if not issues:
                return {
                    "status": "ANALYSIS_COMPLETE",
                    "diagnostic": {
                        "summary": "Aucun problème détecté dans le projet FastAPI malgré l'erreur signalée",
                        "error_type": "unknown",
                        "severity": "medium",
                        "details": error_message
                    },
                    "resolution_action": "NOTIFY_ADMIN",
                    "resolution_details": "L'agent FastAPI n'a pas détecté de problème. Vérification manuelle requise.",
                    "requires_human": True,
                    "timestamp": datetime.datetime.now().isoformat()
                }
            
            # Mappages des types d'erreur
            severity_map = {
                "indentation": "medium",
                "sa_instance_state": "high",
                "router_not_defined": "high",
                "router_prefix_duplicate": "medium"
            }
            
            # Déterminer la gravité
            error_type = issues[0]["error_type"]
            severity = severity_map.get(error_type, "high")
            
            return {
                "status": "ANALYSIS_COMPLETE",
                "diagnostic": {
                    "summary": f"Problème(s) détecté(s) dans le projet FastAPI: {len(issues)} issues",
                    "error_type": error_type,
                    "severity": severity,
                    "details": json.dumps(issues, indent=2)
                },
                "resolution_action": "AUTO_RESOLVE",
                "resolution_method": "fastapi_diagnostic",
                "resolution_details": "L'agent intelligent FastAPI peut réparer ce problème automatiquement",
                "requires_human": False,
                "auto_resolution_ready": True,
                "timestamp": datetime.datetime.now().isoformat()
            }
                
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse FastAPI: {str(e)}")
            return {
                "status": "ERROR",
                "diagnostic": {
                    "summary": f"Erreur lors de l'analyse FastAPI: {str(e)}",
                    "error_type": "analyzer_error",
                    "severity": "high",
                    "details": f"Exception dans l'analyseur FastAPI: {str(e)}"
                },
                "resolution_action": "NOTIFY_ADMIN",
                "requires_human": True,
                "timestamp": datetime.datetime.now().isoformat()
            }
    
    def _analyze_generic_error(self, error_message: str, file_path: Optional[str], context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse une erreur générique avec SmartDebugger."""
        try:
            # Utiliser SmartDebugger pour l'analyse
            analysis = self.smart_debugger.analyze_error(
                error_message=error_message,
                file_path=file_path,
                code_context=json.dumps(context)
            )
            
            # Si l'agent a une solution avec une confiance élevée
            if analysis.get("confidence", 0) > 0.7 and "experience_id" in analysis:
                return {
                    "status": "ANALYSIS_COMPLETE",
                    "diagnostic": {
                        "summary": f"Solution trouvée avec une confiance de {analysis['confidence']:.2f}",
                        "error_type": self._determine_error_type(analysis),
                        "severity": "medium",
                        "details": analysis.get("recommended_solution", "")
                    },
                    "resolution_action": "AUTO_RESOLVE",
                    "resolution_method": "smart_debugger",
                    "resolution_details": "L'agent SmartDebugger peut réparer ce problème",
                    "experience_id": analysis.get("experience_id"),
                    "requires_human": False,
                    "auto_resolution_ready": True,
                    "timestamp": datetime.datetime.now().isoformat()
                }
            else:
                # Confiance insuffisante
                return {
                    "status": "ANALYSIS_COMPLETE",
                    "diagnostic": {
                        "summary": "Analyse complète mais confiance insuffisante pour une correction automatique",
                        "error_type": "unknown",
                        "severity": "medium",
                        "details": analysis.get("recommended_solution", "Aucune solution proposée")
                    },
                    "resolution_action": "SUGGEST_FIX",
                    "resolution_details": f"L'agent recommande: {analysis.get('recommended_solution', 'Intervention manuelle requise')}",
                    "experience_id": analysis.get("experience_id", ""),
                    "confidence": analysis.get("confidence", 0),
                    "requires_human": True,
                    "timestamp": datetime.datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse générique: {str(e)}")
            return {
                "status": "ERROR",
                "diagnostic": {
                    "summary": f"Erreur lors de l'analyse générique: {str(e)}",
                    "error_type": "analyzer_error",
                    "severity": "high",
                    "details": f"Exception dans l'analyseur générique: {str(e)}"
                },
                "resolution_action": "NOTIFY_ADMIN",
                "requires_human": True,
                "timestamp": datetime.datetime.now().isoformat()
            }
    
    def _determine_error_type(self, analysis: Dict[str, Any]) -> str:
        """Détermine le type d'erreur à partir de l'analyse."""
        if not analysis or "recommended_solution" not in analysis:
            return "unknown"
            
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
            return "general"
    
    def auto_resolve(self, diagnostic_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Tente de résoudre automatiquement un problème basé sur le diagnostic.
        
        Args:
            diagnostic_result: Résultat du diagnostic
            
        Returns:
            Résultat de la tentative de résolution
        """
        if not self.initialized:
            logger.warning("Les agents de débogage intelligents ne sont pas disponibles. Résolution impossible.")
            return {
                "success": False,
                "message": "Les agents de débogage intelligents ne sont pas disponibles.",
                "timestamp": datetime.datetime.now().isoformat()
            }
        
        # Récupérer la méthode de résolution et les détails du diagnostic
        resolution_method = diagnostic_result.get("resolution_method", "")
        error_type = diagnostic_result.get("diagnostic", {}).get("error_type", "unknown")
        file_path = None
        
        # Extraire le chemin du fichier des détails
        try:
            details = diagnostic_result.get("diagnostic", {}).get("details", "{}")
            if isinstance(details, str) and details.startswith("{"):
                details_dict = json.loads(details)
                if isinstance(details_dict, list) and len(details_dict) > 0:
                    file_path = details_dict[0].get("file_path", None)
                else:
                    file_path = details_dict.get("file_path", None)
        except:
            # Si l'extraction échoue, chercher le chemin ailleurs
            pass
        
        # Si file_path est toujours None, essayer d'autres sources
        if file_path is None:
            if "file_path" in diagnostic_result:
                file_path = diagnostic_result["file_path"]
            elif "context" in diagnostic_result and "file_path" in diagnostic_result["context"]:
                file_path = diagnostic_result["context"]["file_path"]
        
        if not file_path:
            logger.error("Impossible de déterminer le chemin du fichier pour la résolution")
            return {
                "success": False,
                "message": "Impossible de déterminer le chemin du fichier pour la résolution",
                "timestamp": datetime.datetime.now().isoformat()
            }
        
        try:
            # Choisir la méthode de résolution appropriée
            if resolution_method == "berinia_fixer":
                return self._resolve_with_berinia_fixer(error_type, file_path)
            elif resolution_method == "fastapi_diagnostic":
                return self._resolve_with_fastapi_diagnostic(error_type, file_path)
            elif resolution_method == "smart_debugger":
                return self._resolve_with_smart_debugger(error_type, file_path, diagnostic_result)
            else:
                logger.warning(f"Méthode de résolution inconnue: {resolution_method}")
                return {
                    "success": False,
                    "message": f"Méthode de résolution inconnue: {resolution_method}",
                    "timestamp": datetime.datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"Erreur lors de la résolution: {str(e)}")
            return {
                "success": False,
                "message": f"Erreur lors de la résolution: {str(e)}",
                "timestamp": datetime.datetime.now().isoformat()
            }
    
    def _resolve_with_berinia_fixer(self, error_type: str, file_path: str) -> Dict[str, Any]:
        """Résout un problème à l'aide de BeriniaIntelligentFixer."""
        logger.info(f"Résolution avec BeriniaIntelligentFixer: {error_type} dans {file_path}")
        
        # Fixer les problèmes détectés
        fixes = self.berinia_fixer.fix_issues(auto_approve=True)
        
        if not fixes:
            return {
                "success": False,
                "message": "Aucune correction n'a pu être appliquée",
                "timestamp": datetime.datetime.now().isoformat()
            }
        
        # Redémarrer le service si des corrections ont été appliquées
        restart_result = self.berinia_fixer.restart_service()
        
        return {
            "success": True,
            "message": f"Corrections appliquées avec succès: {len(fixes)} problèmes résolus",
            "restart_success": restart_result,
            "fixes_count": len(fixes),
            "timestamp": datetime.datetime.now().isoformat()
        }
    
    def _resolve_with_fastapi_diagnostic(self, error_type: str, file_path: str) -> Dict[str, Any]:
        """Résout un problème à l'aide de FastAPIDiagnostic."""
        logger.info(f"Résolution avec FastAPIDiagnostic: {error_type} dans {file_path}")
        
        # Déterminer le projet à analyser
        project_path = "/root/berinia/backend"
        if "/berinia/" in file_path:
            project_path = "/root/berinia/backend"
        
        # Créer un nouvel objet diagnostic pour éviter les conflits d'état
        diagnostic = FastAPIDiagnostic(project_path=project_path)
        
        # Récupérer les problèmes
        issues = diagnostic.analyze_all()
        
        if not issues:
            return {
                "success": False,
                "message": "Aucun problème détecté lors de l'analyse",
                "timestamp": datetime.datetime.now().isoformat()
            }
        
        # Appliquer les corrections
        fixes = diagnostic.fix_issues(auto_fix=True)
        
        if not fixes:
            return {
                "success": False,
                "message": "Aucune correction n'a pu être appliquée",
                "timestamp": datetime.datetime.now().isoformat()
            }
        
        return {
            "success": True,
            "message": f"Corrections appliquées avec succès: {len(fixes)} problèmes résolus",
            "fixes_count": len(fixes),
            "timestamp": datetime.datetime.now().isoformat()
        }
    
    def _resolve_with_smart_debugger(self, error_type: str, file_path: str, diagnostic_result: Dict[str, Any]) -> Dict[str, Any]:
        """Résout un problème à l'aide de SmartDebugger."""
        logger.info(f"Résolution avec SmartDebugger: {error_type} dans {file_path}")
        
        # Appliquer la correction
        result = self.smart_debugger.apply_fix(error_type, file_path)
        
        if not result["success"]:
            return {
                "success": False,
                "message": result["message"],
                "timestamp": datetime.datetime.now().isoformat()
            }
        
        return {
            "success": True,
            "message": result["message"],
            "experience_id": diagnostic_result.get("experience_id"),
            "timestamp": datetime.datetime.now().isoformat()
        }
    
    def process_feedback(self, memory_id: str, success: bool) -> bool:
        """
        Traite un retour d'information sur une correction précédente.
        
        Args:
            memory_id: ID de la mémoire
            success: Si la correction a réussi
            
        Returns:
            True si le feedback a été enregistré avec succès
        """
        if not self.initialized or self.smart_debugger is None:
            logger.warning("SmartDebugger n'est pas disponible. Impossible d'enregistrer le feedback.")
            return False
        
        try:
            return self.smart_debugger.save_feedback(
                memory_id, 
                "positive" if success else "negative"
            )
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement du feedback: {str(e)}")
            return False


# Instancier l'adaptateur
intelligent_debug_adapter = IntelligentDebugAdapter()

# Fonctions d'interface pour le DebuggerAgent
def analyze_error(failed_agent: str, error_message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Interface pour l'analyse d'erreur utilisée par le DebuggerAgent.
    
    Args:
        failed_agent: Nom de l'agent qui a échoué
        error_message: Message d'erreur
        context: Contexte supplémentaire
        
    Returns:
        Résultat de l'analyse
    """
    if context is None:
        context = {}
    
    return intelligent_debug_adapter.analyze_error(failed_agent, error_message, context)

def auto_resolve(diagnostic_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Interface pour la résolution automatique utilisée par le DebuggerAgent.
    
    Args:
        diagnostic_result: Résultat du diagnostic
        
    Returns:
        Résultat de la résolution
    """
    return intelligent_debug_adapter.auto_resolve(diagnostic_result)

def process_feedback(memory_id: str, success: bool) -> bool:
    """
    Interface pour le traitement des retours utilisée par le DebuggerAgent.
    
    Args:
        memory_id: ID de la mémoire
        success: Si la correction a réussi
        
    Returns:
        True si le feedback a été enregistré avec succès
    """
    return intelligent_debug_adapter.process_feedback(memory_id, success)
