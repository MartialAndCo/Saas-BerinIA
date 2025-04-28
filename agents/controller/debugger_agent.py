import json
import datetime
import os
import time
from colorama import Fore, Style
from agents.base.base import AgentBase
from logs.agent_logger import log_agent
from utils.llm import ask_gpt_4_1

class DebuggerAgent(AgentBase):
    """
    Agent spécialisé dans le diagnostic et la résolution des erreurs.
    S'active quand un agent de la chaîne rencontre une erreur et analyse
    la situation pour prendre une décision adaptée au type de problème.
    """
    def __init__(self):
        super().__init__("DebuggerAgent")
        self.debug_log_path = "logs/debugger"
        self._ensure_debug_folder_exists()
        self.issue_history = self._load_issue_history()
        
    def _ensure_debug_folder_exists(self):
        """Assure que le dossier pour les logs de débogage existe"""
        if not os.path.exists(self.debug_log_path):
            os.makedirs(self.debug_log_path, exist_ok=True)
    
    def _load_issue_history(self):
        """Charge l'historique des problèmes rencontrés"""
        history_path = os.path.join(self.debug_log_path, "issue_history.json")
        if os.path.exists(history_path):
            try:
                with open(history_path, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"[{self.name}] ⚠️ Fichier d'historique des problèmes corrompu, création d'un nouveau")
        
        # Créer un nouvel historique
        history = {
            "issues": [],
            "resolutions": [],
            "patterns": {},
            "last_updated": datetime.datetime.now().isoformat()
        }
        
        with open(history_path, "w") as f:
            json.dump(history, f, indent=2)
            
        return history
        
    def _save_issue_history(self):
        """Sauvegarde l'historique des problèmes mis à jour"""
        history_path = os.path.join(self.debug_log_path, "issue_history.json")
        self.issue_history["last_updated"] = datetime.datetime.now().isoformat()
        
        with open(history_path, "w") as f:
            json.dump(self.issue_history, f, indent=2)
    
    def _save_analysis_report(self, report):
        """Sauvegarde un rapport d'analyse détaillé"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(self.debug_log_path, f"debug_report_{timestamp}.json")
        
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
            
        return report_path
        
    def run(self, input_data: dict) -> dict:
        print(f"[{self.name}] 🔍 Analyse des erreurs dans la chaîne d'agents...")
        
        # Extraire les informations clés
        error_agent = input_data.get("failed_agent")
        error_message = input_data.get("error_message", "Erreur non spécifiée")
        error_status = input_data.get("error_status", "UNKNOWN")
        agent_results = input_data.get("agent_results", {})
        decision = input_data.get("brain_decision", {})
        context = input_data.get("context", {})
        error_type = input_data.get("error_type", "FUNCTIONAL")  # FUNCTIONAL, TECHNICAL, DATA
        
        # Créer un rapport initial
        report = {
            "timestamp": datetime.datetime.now().isoformat(),
            "failed_agent": error_agent,
            "error_message": error_message,
            "error_status": error_status,
            "agent_results": agent_results,
            "brain_decision": decision,
            "context": context,
            "error_type": error_type,
            "analysis": {},
            "resolution": {},
            "system_impact": "UNKNOWN"
        }
        
        # Vérifier si nous avons assez d'informations pour procéder
        if not error_agent:
            report["analysis"]["conclusion"] = "Informations insuffisantes pour l'analyse"
            report["resolution"]["action"] = "NOTIFY_ADMIN"
            report["resolution"]["message"] = "Impossible d'analyser l'erreur: agent défaillant non spécifié"
            report["system_impact"] = "LOW"
            
            # Enregistrer le rapport et retourner
            report_path = self._save_analysis_report(report)
            print(f"[{self.name}] ⚠️ Informations insuffisantes pour l'analyse. Rapport: {report_path}")
            
            return {
                "status": "COMPLETED",
                "resolution": "INCOMPLETE_ANALYSIS",
                "report_path": report_path,
                "recommendation": "NOTIFY_ADMIN",
                "error_details": "Informations insuffisantes"
            }
        
        print(f"[{self.name}] 🧩 Analyse de l'erreur sur l'agent {error_agent}: {error_message}")
        
        # Récupérer les résultats des agents précédents dans la chaîne
        chain_analysis = self._analyze_agent_chain(error_agent, agent_results)
        report["analysis"]["chain_analysis"] = chain_analysis
        
        # Analyser l'erreur spécifique en fonction de l'agent
        error_analysis = self._analyze_specific_error(error_agent, error_message, agent_results)
        report["analysis"]["error_analysis"] = error_analysis
        
        # Rechercher des patterns récurrents
        pattern_match = self._check_for_patterns(error_agent, error_message)
        report["analysis"]["pattern_match"] = pattern_match
        
        # Analyser si l'erreur est critique ou non
        criticality = self._determine_criticality(error_agent, error_message, chain_analysis)
        report["analysis"]["criticality"] = criticality
        
        # Générer un rapport de diagnostic
        diagnostic = self._generate_diagnostic(report["analysis"])
        report["analysis"]["diagnostic"] = diagnostic
        
        # Déterminer l'impact sur le système
        impact = self._determine_system_impact(criticality, error_agent)
        report["system_impact"] = impact
        
        # Proposer une résolution
        resolution = self._propose_resolution(report["analysis"], agent_results, decision)
        report["resolution"] = resolution
        
        # Sauvegarder le rapport d'analyse
        report_path = self._save_analysis_report(report)
        print(f"[{self.name}] 📊 Analyse terminée. Rapport sauvegardé: {report_path}")
        
        # Mettre à jour l'historique des problèmes
        self._update_issue_history(report)
        
        # Préparer la réponse
        result = {
            "status": "COMPLETED",
            "resolution_action": resolution["action"],
            "resolution_details": resolution["details"],
            "system_impact": impact,
            "report_path": report_path,
            "diagnostic": diagnostic,
            "recommendation": resolution["recommendation"],
            "requires_human": resolution.get("requires_human", False)
        }
        
        # Exécuter la résolution automatique si possible
        if resolution["action"] == "AUTO_RESOLVE" and not resolution.get("requires_human", False):
            auto_resolve_result = self._execute_auto_resolution(resolution, error_agent, agent_results, decision)
            result["auto_resolve_result"] = auto_resolve_result
            
        # Enregistrer les logs
        log_agent(self.name, input_data, result)
        
        return result
    
    def _analyze_agent_chain(self, error_agent, agent_results):
        """Analyse la chaîne d'agents et les dépendances"""
        chain_analysis = {
            "chain_intact_before_error": True,
            "dependencies_satisfied": True,
            "failed_dependencies": [],
            "successful_agents": [],
            "agents_with_warnings": [],
            "chain_break_point": error_agent
        }
        
        # Définir l'ordre de dépendance des agents
        dependency_chain = {
            "StrategyAgent": [],  # Aucune dépendance
            "PlanningAgent": ["StrategyAgent"],  # Dépend de StrategyAgent
            "CampaignStarterAgent": ["StrategyAgent", "PlanningAgent"],  # Dépend de StrategyAgent et PlanningAgent
            "ScraperAgent": ["CampaignStarterAgent"],  # Dépend de CampaignStarterAgent
            "CleanerAgent": ["ScraperAgent"],  # Dépend de ScraperAgent
            "ClassifierAgent": ["CleanerAgent"]  # Dépend de CleanerAgent
        }
        
        # Vérifier les dépendances de l'agent qui a échoué
        if error_agent in dependency_chain:
            agent_dependencies = dependency_chain[error_agent]
            
            # Vérifier si toutes les dépendances ont été exécutées avec succès
            for dep in agent_dependencies:
                if dep not in agent_results:
                    chain_analysis["dependencies_satisfied"] = False
                    chain_analysis["failed_dependencies"].append(f"{dep}: Non exécuté")
                elif agent_results[dep].get("status") == "FAILED":
                    chain_analysis["dependencies_satisfied"] = False
                    chain_analysis["failed_dependencies"].append(f"{dep}: Échec - {agent_results[dep].get('error', 'Erreur non spécifiée')}")
                elif "error" in agent_results[dep] and not agent_results[dep].get("status") == "COMPLETED":
                    chain_analysis["agents_with_warnings"].append(f"{dep}: Avertissement - {agent_results[dep].get('error')}")
                else:
                    chain_analysis["successful_agents"].append(dep)
        
        return chain_analysis
    
    def _analyze_specific_error(self, error_agent, error_message, agent_results):
        """Analyse l'erreur spécifique en fonction de l'agent"""
        analysis = {
            "error_category": "UNKNOWN",
            "probable_cause": "UNKNOWN",
            "potential_solutions": []
        }
        
        # Analyser l'erreur du StrategyAgent
        if error_agent == "StrategyAgent":
            if error_message == "Aucune niche fournie" or "niche" in error_message.lower():
                analysis["error_category"] = "DATA_MISSING"
                analysis["probable_cause"] = "Le StrategyAgent n'a pas généré de niche valide"
                analysis["potential_solutions"] = [
                    "Regénérer une niche automatiquement",
                    "Réexécuter le StrategyAgent avec un prompt modifié",
                    "Fournir une niche par défaut"
                ]
        
        # Analyser l'erreur du CampaignStarterAgent
        elif error_agent == "CampaignStarterAgent":
            if "niche" in error_message.lower() and "valid" in error_message.lower():
                analysis["error_category"] = "DATA_VALIDATION"
                analysis["probable_cause"] = "StrategyAgent a fourni une niche invalide ou nulle"
                
                # Vérifier si le StrategyAgent a fourni une niche
                strategy_result = agent_results.get("StrategyAgent", {})
                if strategy_result.get("niche") is None:
                    analysis["detailed_cause"] = "Le StrategyAgent a retourné une niche NULL"
                    analysis["potential_solutions"] = [
                        "Réexécuter le StrategyAgent avec un prompt différent",
                        "Utiliser une niche par défaut ('avocats' ou 'consultants')",
                        "Corriger le problème dans le code du StrategyAgent (possible bug)"
                    ]
                else:
                    analysis["detailed_cause"] = f"La niche '{strategy_result.get('niche')}' est invalide"
                    analysis["potential_solutions"] = [
                        "Valider la niche manuellement",
                        "Utiliser une niche alternative"
                    ]
        
        # Analyser les erreurs du ScraperAgent
        elif error_agent == "ScraperAgent":
            analysis["error_category"] = "SCRAPER_ERROR"
            if "niche" in error_message.lower():
                analysis["probable_cause"] = "Absence de niche pour le scraping"
                analysis["potential_solutions"] = [
                    "Fournir une niche valide depuis le StrategyAgent",
                    "Utiliser des données de test prédéfinies",
                    "Passer directement à l'étape suivante avec des données simulées"
                ]
        
        # Analyser les erreurs du CleanerAgent
        elif error_agent == "CleanerAgent":
            analysis["error_category"] = "DATA_PROCESSING"
            if "aucune donnée" in error_message.lower():
                analysis["probable_cause"] = "Absence de données à nettoyer"
                analysis["potential_solutions"] = [
                    "Vérifier que le ScraperAgent a bien fourni des données",
                    "Utiliser des données de test",
                    "Ignorer cette étape et passer à la suivante"
                ]
        
        # Autres agents
        else:
            # Déterminer la catégorie en fonction du message
            if "données" in error_message.lower() or "data" in error_message.lower():
                analysis["error_category"] = "DATA_ERROR"
            elif "connexion" in error_message.lower() or "réseau" in error_message.lower() or "api" in error_message.lower():
                analysis["error_category"] = "CONNECTION_ERROR"
            elif "permission" in error_message.lower() or "accès" in error_message.lower():
                analysis["error_category"] = "PERMISSION_ERROR"
            elif "format" in error_message.lower() or "type" in error_message.lower():
                analysis["error_category"] = "FORMAT_ERROR"
            else:
                analysis["error_category"] = "GENERAL_ERROR"
        
        return analysis
    
    def _check_for_patterns(self, error_agent, error_message):
        """Vérifie si l'erreur correspond à un pattern connu"""
        pattern_match = {
            "known_pattern": False,
            "pattern_id": None,
            "pattern_name": None,
            "occurrences": 0,
            "last_occurrence": None,
            "resolution_success_rate": 0
        }
        
        # Récupérer les patterns connus depuis l'historique
        patterns = self.issue_history.get("patterns", {})
        
        # Vérifier chaque pattern
        for pattern_id, pattern in patterns.items():
            if pattern["agent"] == error_agent and error_message.lower() in pattern["error_signature"].lower():
                pattern_match["known_pattern"] = True
                pattern_match["pattern_id"] = pattern_id
                pattern_match["pattern_name"] = pattern.get("name", "Pattern sans nom")
                pattern_match["occurrences"] = pattern.get("occurrences", 0)
                pattern_match["last_occurrence"] = pattern.get("last_occurrence")
                
                # Calculer le taux de réussite des résolutions
                successful_resolutions = pattern.get("successful_resolutions", 0)
                total_resolutions = pattern.get("total_resolutions", 0)
                
                if total_resolutions > 0:
                    pattern_match["resolution_success_rate"] = successful_resolutions / total_resolutions
                    
                break
        
        return pattern_match
    
    def _determine_criticality(self, error_agent, error_message, chain_analysis):
        """Détermine si l'erreur est critique ou non"""
        criticality = {
            "level": "MEDIUM",  # LOW, MEDIUM, HIGH, CRITICAL
            "explanation": "",
            "blocking": True,
            "requires_immediate_attention": False
        }
        
        # Erreurs du StrategyAgent sont généralement critiques
        if error_agent == "StrategyAgent":
            if error_message.lower() in ["aucune niche fournie", "niche invalide", "échec de génération"]:
                criticality["level"] = "HIGH"
                criticality["explanation"] = "Le StrategyAgent est essentiel pour démarrer la chaîne - sans niche, tout le flux est bloqué"
                criticality["blocking"] = True
                criticality["requires_immediate_attention"] = True
            else:
                criticality["level"] = "MEDIUM"
                criticality["explanation"] = "Problème avec le StrategyAgent mais potentiellement corrigible"
        
        # Erreurs du CampaignStarterAgent
        elif error_agent == "CampaignStarterAgent":
            if "niche" in error_message.lower():
                criticality["level"] = "MEDIUM"
                criticality["explanation"] = "Le CampaignStarterAgent nécessite une niche valide pour démarrer"
                criticality["blocking"] = True
                criticality["requires_immediate_attention"] = False
        
        # Les erreurs qui impliquent explicitement des dépendances manquantes sont moins critiques
        if not chain_analysis["dependencies_satisfied"]:
            criticality["explanation"] += " (Causé par des dépendances non satisfaites)"
            
            # Si l'erreur est simplement due à une chaîne de dépendances rompue,
            # elle n'est pas aussi critique que des erreurs fondamentales
            if criticality["level"] == "HIGH":
                criticality["level"] = "MEDIUM"
                
        return criticality
    
    def _generate_diagnostic(self, analysis):
        """Génère un diagnostic complet basé sur l'analyse"""
        # Construit un diagnostic en langage naturel
        chain_analysis = analysis.get("chain_analysis", {})
        error_analysis = analysis.get("error_analysis", {})
        criticality = analysis.get("criticality", {})
        
        # Construire le diagnostic principal
        diagnostic = {
            "summary": "",
            "root_cause": "",
            "impact": "",
            "recommendation": ""
        }
        
        # Résumé
        if criticality.get("level") == "HIGH":
            diagnostic["summary"] = f"Erreur critique détectée dans l'agent {chain_analysis.get('chain_break_point')}"
        elif criticality.get("level") == "MEDIUM":
            diagnostic["summary"] = f"Problème significatif détecté dans l'agent {chain_analysis.get('chain_break_point')}"
        else:
            diagnostic["summary"] = f"Problème mineur détecté dans l'agent {chain_analysis.get('chain_break_point')}"
        
        # Cause racine
        if error_analysis.get("probable_cause") != "UNKNOWN":
            diagnostic["root_cause"] = f"Cause probable: {error_analysis.get('probable_cause')}"
            if "detailed_cause" in error_analysis:
                diagnostic["root_cause"] += f". {error_analysis.get('detailed_cause')}"
        else:
            diagnostic["root_cause"] = "Cause indéterminée"
        
        # Impact
        if chain_analysis.get("chain_intact_before_error", True):
            diagnostic["impact"] = "Les agents précédents dans la chaîne ont fonctionné normalement"
        else:
            diagnostic["impact"] = "La chaîne d'agents était déjà compromise avant cette erreur"
            
        if criticality.get("blocking", True):
            diagnostic["impact"] += ", mais ce problème bloque l'exécution de la chaîne"
        else:
            diagnostic["impact"] += " et ce problème n'empêche pas la poursuite de l'exécution"
        
        # Recommandation
        if error_analysis.get("potential_solutions"):
            solutions = error_analysis.get("potential_solutions")
            diagnostic["recommendation"] = f"Solutions suggérées: {', '.join(solutions[:2])}"
            
            if len(solutions) > 2:
                diagnostic["recommendation"] += f" (et {len(solutions) - 2} autre(s) option(s))"
        else:
            if criticality.get("requires_immediate_attention", False):
                diagnostic["recommendation"] = "Intervention humaine requise pour résoudre ce problème"
            else:
                diagnostic["recommendation"] = "Une solution automatique peut être tentée"
        
        return diagnostic
    
    def _determine_system_impact(self, criticality, error_agent):
        """Détermine l'impact sur le système global"""
        # Par défaut, mapper les niveaux de criticité aux impacts système
        if criticality.get("level") == "CRITICAL":
            return "SEVERE"
        elif criticality.get("level") == "HIGH":
            return "HIGH"
        elif criticality.get("level") == "MEDIUM":
            return "MODERATE"
        elif criticality.get("level") == "LOW":
            return "LOW"
        else:
            return "UNKNOWN"
    
    def _propose_resolution(self, analysis, agent_results, decision):
        """Propose une résolution basée sur l'analyse"""
        error_analysis = analysis.get("error_analysis", {})
        criticality = analysis.get("criticality", {})
        diagnostic = analysis.get("diagnostic", {})
        
        resolution = {
            "action": "UNKNOWN",  # NOTIFY_ADMIN, AUTO_RESOLVE, RESTART, ABORT, CONTINUE_WITH_WARNING
            "details": "",
            "recommendation": "",
            "requires_human": False,
            "confidence": 0.0,
            "retry_agent": None,
            "retry_with_modified_input": False,
            "modified_input": {}
        }
        
        # Décisions basées sur la catégorie d'erreur et la criticité
        error_category = error_analysis.get("error_category", "UNKNOWN")
        criticality_level = criticality.get("level", "MEDIUM")
        
        # ERREURS DE DONNÉES MANQUANTES
        if error_category == "DATA_MISSING":
            # Cas particulier: StrategyAgent n'a pas généré de niche
            if analysis.get("chain_analysis", {}).get("chain_break_point") == "StrategyAgent":
                resolution["action"] = "AUTO_RESOLVE"
                resolution["details"] = "Générer automatiquement une niche par défaut pour démarrer le système"
                resolution["recommendation"] = "Utiliser une niche prédéfinie 'Avocats' comme solution de secours"
                resolution["confidence"] = 0.8
                resolution["retry_agent"] = "StrategyAgent"
                resolution["retry_with_modified_input"] = True
                resolution["modified_input"] = {
                    "niche": "Avocats",
                    "justification": "Niche par défaut générée par le DebuggerAgent pour résoudre un problème de démarrage",
                    "potentiel_conversion": "moyen"
                }
            else:
                resolution["action"] = "NOTIFY_ADMIN"
                resolution["details"] = "Données manquantes qui nécessitent une intervention humaine"
                resolution["requires_human"] = True
                resolution["confidence"] = 0.7
                
        # ERREURS DE VALIDATION DE DONNÉES
        elif error_category == "DATA_VALIDATION":
            # Cas particulier: CampaignStarterAgent a besoin d'une niche valide
            if analysis.get("chain_analysis", {}).get("chain_break_point") == "CampaignStarterAgent":
                # Vérifier si le StrategyAgent a effectivement échoué à fournir une niche
                strategy_result = agent_results.get("StrategyAgent", {})
                if strategy_result.get("niche") is None:
                    resolution["action"] = "AUTO_RESOLVE"
                    resolution["details"] = "Fournir une niche valide au CampaignStarterAgent"
                    resolution["recommendation"] = "Réexécuter avec une niche par défaut 'Consultants'"
                    resolution["confidence"] = 0.85
                    resolution["retry_agent"] = "CampaignStarterAgent"
                    resolution["retry_with_modified_input"] = True
                    resolution["modified_input"] = {
                        "operation": "start_new_campaign",
                        "validated_niche": "Consultants",
                        "justification": "Niche fournie par le DebuggerAgent pour résoudre un problème de démarrage"
                    }
                else:
                    resolution["action"] = "NOTIFY_ADMIN"
                    resolution["details"] = f"La niche '{strategy_result.get('niche')}' est rejetée par le CampaignStarterAgent"
                    resolution["requires_human"] = True
                    resolution["confidence"] = 0.75
            else:
                resolution["action"] = "NOTIFY_ADMIN"
                resolution["details"] = "Problème de validation de données qui nécessite une intervention humaine"
                resolution["requires_human"] = True
                resolution["confidence"] = 0.7
        
        # ERREURS GÉNÉRALES
        else:
            if criticality_level in ["CRITICAL", "HIGH"]:
                resolution["action"] = "NOTIFY_ADMIN"
                resolution["details"] = "Erreur critique qui nécessite une intervention humaine"
                resolution["requires_human"] = True
                resolution["confidence"] = 0.9
            elif criticality_level == "MEDIUM":
                resolution["action"] = "NOTIFY_ADMIN"
                resolution["details"] = "Problème significatif qui peut nécessiter une intervention humaine"
                resolution["requires_human"] = True
                resolution["confidence"] = 0.7
            else:
                resolution["action"] = "CONTINUE_WITH_WARNING"
                resolution["details"] = "Problème mineur qui n'empêche pas la poursuite de l'exécution"
                resolution["requires_human"] = False
                resolution["confidence"] = 0.8
        
        return resolution
    
    def _update_issue_history(self, report):
        """Met à jour l'historique des problèmes avec ce nouveau rapport"""
        # Ajouter le problème à l'historique
        issue_entry = {
            "timestamp": report["timestamp"],
            "agent": report["failed_agent"],
            "error_message": report["error_message"],
            "error_type": report["error_type"],
            "system_impact": report["system_impact"],
            "resolution_action": report["resolution"]["action"],
            "report_path": report.get("report_path", "")
        }
        
        self.issue_history["issues"].append(issue_entry)
        
        # Si c'est un pattern connu, mettre à jour ses statistiques
        pattern_match = report["analysis"].get("pattern_match", {})
        if pattern_match.get("known_pattern", False) and pattern_match.get("pattern_id"):
            pattern_id = pattern_match["pattern_id"]
            
            # Incrementer le compteur d'occurrences
            if pattern_id in self.issue_history["patterns"]:
                self.issue_history["patterns"][pattern_id]["occurrences"] += 1
                self.issue_history["patterns"][pattern_id]["last_occurrence"] = report["timestamp"]
        else:
            # Créer un nouveau pattern
            pattern_id = f"PATTERN_{len(self.issue_history['patterns']) + 1}"
            self.issue_history["patterns"][pattern_id] = {
                "agent": report["failed_agent"],
                "error_signature": report["error_message"],
                "name": f"Erreur {report['failed_agent']} - {report['analysis'].get('error_analysis', {}).get('error_category', 'UNKNOWN')}",
                "created_at": report["timestamp"],
                "last_occurrence": report["timestamp"],
                "occurrences": 1,
                "successful_resolutions": 0,
                "total_resolutions": 0
            }
        
        # Sauvegarder l'historique mis à jour
        self._save_issue_history()
    
    def _execute_auto_resolution(self, resolution, error_agent, agent_results, decision):
        """Exécute la résolution automatique si possible"""
        result = {
            "success": False,
            "action_taken": resolution["action"],
            "details": "",
            "retry_result": None
        }
        
        # Si la résolution nécessite de réexécuter un agent
        if resolution["retry_agent"] and resolution["retry_with_modified_input"]:
            agent_to_retry = resolution["retry_agent"]
            modified_input = resolution["modified_input"]
            
            print(f"[{self.name}] 🔄 Tentative de résolution automatique: Réexécution de {agent_to_retry} avec entrée modifiée")
            
            try:
                # Selon l'agent à réexécuter, instancier et appeler l'agent approprié
                if agent_to_retry == "StrategyAgent":
                    from agents.controller.strategy_agent import StrategyAgent
                    agent = StrategyAgent()
                    
                    # Ajouter les paramètres communs
                    params = {
                        "initiated_by": "DebuggerAgent",
                        "brain_decision": decision,
                        "approach": "initial"
                    }
                    
                    # Fusionner avec les paramètres modifiés
                    params.update(modified_input)
                    
                    # Exécuter l'agent
                    retry_result = agent.run(params)
                    
                    result["success"] = True
                    result["details"] = f"StrategyAgent réexécuté avec succès et a fourni la niche '{retry_result.get('niche')}'"
                    result["retry_result"] = retry_result
                
                elif agent_to_retry == "CampaignStarterAgent":
                    from agents.controller.campaign_starter_agent import CampaignStarterAgent
                    agent = CampaignStarterAgent()
                    
                    # Ajouter les paramètres communs
                    params = {
                        "initiated_by": "DebuggerAgent",
                        "brain_decision": decision
                    }
                    
                    # Fusionner avec les paramètres modifiés
                    params.update(modified_input)
                    
                    # Exécuter l'agent
                    retry_result = agent.run(params)
                    
                    result["success"] = True
                    result["details"] = f"CampaignStarterAgent réexécuté avec la niche fournie"
                    result["retry_result"] = retry_result
                
                else:
                    result["success"] = False
                    result["details"] = f"Agent {agent_to_retry} non pris en charge pour la résolution automatique"
            
            except ImportError as e:
                result["success"] = False
                result["details"] = f"Erreur d'importation de l'agent {agent_to_retry}: {str(e)}"
                print(f"[{self.name}] ❌ Erreur d'importation: {str(e)}")
            
            except Exception as e:
                result["success"] = False
                result["details"] = f"Erreur lors de l'exécution de {agent_to_retry}: {str(e)}"
                print(f"[{self.name}] ❌ Erreur d'exécution: {str(e)}")
        
        else:
            result["details"] = "Aucune action de résolution automatique disponible"
        
        return result
