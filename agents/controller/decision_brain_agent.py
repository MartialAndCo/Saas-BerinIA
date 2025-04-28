import json
import time
import datetime
import logging
import random
import colorama
from colorama import Fore, Style
from agents.base.base import AgentBase
from db.postgres import get_campaign_data, get_campaign_summary, get_active_campaigns, PostgresClient
from memory.qdrant import QdrantClient, get_campaign_knowledge, get_underexplored_niches
from utils.llm import ask_gpt_4_1
from logs.agent_logger import log_agent

# Initialiser colorama pour les logs colorés
colorama.init()

# Configuration du logging spécifique au DecisionBrainAgent
brain_logger = logging.getLogger("DecisionBrainAgent")
brain_logger.setLevel(logging.INFO)

# Créer un handler pour les fichiers de log
timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
brain_log_file = f"logs/DecisionBrainAgent_{timestamp}.log"
file_handler = logging.FileHandler(brain_log_file)
file_handler.setLevel(logging.INFO)

# Formater les logs
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
brain_logger.addHandler(file_handler)

class DecisionBrainAgent(AgentBase):
    def __init__(self):
        super().__init__("DecisionBrainAgent")
        self.log_prefix = f"{Fore.CYAN}[🧠 BRAIN]{Style.RESET_ALL}"
        self.thinking_steps = []
        self.decision_history = []
        
    def _pretty_log(self, message, level="INFO", emoji="💭", color=Fore.CYAN):
        """Affiche des logs estéthiques avec émojis et couleurs"""
        formatted = f"{color}{self.log_prefix} {emoji} {message}{Style.RESET_ALL}"
        print(formatted)
        
        # Enregistrer dans le fichier de log (sans les codes couleur)
        plain_message = f"[BRAIN] {emoji} {message}"
        if level == "INFO":
            brain_logger.info(plain_message)
        elif level == "WARNING":
            brain_logger.warning(plain_message)
        elif level == "ERROR":
            brain_logger.error(plain_message)
        
        # Ajouter aux étapes de réflexion
        if emoji == "💭":
            self.thinking_steps.append(message)

    def run(self, input_data: dict = {}) -> dict:
        start_time = time.time()
        self._pretty_log("========== DÉCISION STRATÉGIQUE ==========", emoji="🧠", color=Fore.MAGENTA)
        self._pretty_log("Début du processus de raisonnement stratégique global", emoji="🔄")
        
        # Pour traquer l'exécution des agents subordonnés
        agent_results = {}
        
        # Vider les étapes de réflexion pour cette nouvelle exécution
        self.thinking_steps = []
        
        # Analyser le contexte d'entrée
        operation = input_data.get("operation", "evaluate_global_strategy")
        self._pretty_log(f"Opération demandée: {operation}", emoji="📋")
        
        # Récupération des données réelles
        self._pretty_log("Récupération des données de campagnes passées et actives...", emoji="🔍")
        # Utiliser la fonction get_campaign_data qui retourne des listes vides s'il n'y a pas de données
        past_campaigns, active_campaigns = get_campaign_data()
        
        # Récupérer aussi le résumé de campagne pour les métriques
        campaign_summary = get_campaign_summary()
        
        self._pretty_log(f"Campagnes passées: {len(past_campaigns)} | Campagnes actives: {len(active_campaigns)}", emoji="📊")
        
        # Analyse des niches inexploitées
        self._pretty_log("Interrogation de la mémoire vectorielle pour niches inexploitées...", emoji="🧮")
        
        # Utiliser la fonction get_underexplored_niches qui retourne une liste vide s'il n'y a pas de données
        unexplored_niches = get_underexplored_niches()
        
        self._pretty_log(f"Découverte de {len(unexplored_niches)} opportunités inexploitées", emoji="💡")
        
        # Construction du prompt avec des instructions détaillées
        self._pretty_log("Construction du prompt de décision stratégique...", emoji="⚙️")
        prompt = f"""
Tu es le cerveau de BerinIA, le système d'intelligence artificielle qui prend les décisions stratégiques de haut niveau.

## CONTEXTE ACTUEL
Voici les campagnes passées :
{json.dumps(past_campaigns, indent=2)}

Voici les campagnes en cours :
{json.dumps(active_campaigns, indent=2)}

Voici les opportunités inexploitées (issues de Qdrant) :
{json.dumps(unexplored_niches, indent=2)}

## TA MISSION DE HAUT NIVEAU
En tant que cerveau décisionnel du système, tu dois :

1. Analyser les performances des campagnes passées et actives
2. Évaluer le potentiel des niches inexploitées
3. Prendre l'UNE des décisions stratégiques suivantes :
   a) CONTINUER une campagne existante qui montre du potentiel
   b) DÉMARRER une nouvelle campagne (sans choisir la niche toi-même)

## PROCESSUS DÉCISIONNEL
Ton raisonnement doit inclure :
- Un examen des indicateurs clés de performance des campagnes existantes
- Une évaluation de la saturation du marché dans les niches actuelles
- Une considération des ressources système disponibles
- Une projection des résultats potentiels

## FORMAT DE RÉPONSE ATTENDU
- decision_process: [Détaille en 4-5 points ton processus de réflexion]
- action: "continuer" | "nouvelle"
- campagne_cible: [ID ou nom de campagne si continuer]
- commentaire: [Explication stratégique détaillée]
- priorité: [haute|moyenne|basse]
- agents_à_impliquer: [Liste des agents qui devront exécuter cette décision]
"""
        
        # Mesurer le temps de réflexion
        thinking_start = time.time()
        self._pretty_log("Réflexion stratégique en cours (GPT-4.1)...", emoji="💭")
        
        # Demander la décision à GPT-4.1
        decision_text = ask_gpt_4_1(prompt)
        
        # Convertir la réponse JSON en dictionnaire Python
        try:
            # Si la réponse contient des délimiteurs de code JSON, extraire uniquement le JSON
            if isinstance(decision_text, str):
                if "```json" in decision_text:
                    json_start = decision_text.find("```json") + 7
                    json_end = decision_text.find("```", json_start)
                    if json_end > json_start:
                        decision_text = decision_text[json_start:json_end].strip()
                elif "```" in decision_text:
                    json_start = decision_text.find("```") + 3
                    json_end = decision_text.find("```", json_start)
                    if json_end > json_start:
                        decision_text = decision_text[json_start:json_end].strip()
                
                # Parser le JSON
                decision = json.loads(decision_text)
            else:
                # Si c'est déjà un dictionnaire, l'utiliser directement
                decision = decision_text
                
        except json.JSONDecodeError as e:
            self._pretty_log(f"Erreur lors du parsing de la réponse JSON: {str(e)}", emoji="❌", level="ERROR", color=Fore.RED)
            self._pretty_log(f"Réponse brute: {decision_text[:200]}...", emoji="📝", level="ERROR", color=Fore.RED)
            decision = {
                "error": f"Impossible de parser le JSON: {str(e)}",
                "action": "nouvelle",  # Action par défaut
                "priorité": "haute",
                "commentaire": "Erreur de traitement, mais nous recommandons de démarrer une nouvelle campagne par défaut.",
                "agents_à_impliquer": ["StrategyAgent", "PlanningAgent", "CampaignStarterAgent"]
            }
        
        thinking_time = time.time() - thinking_start
        self._pretty_log(f"Décision prise en {thinking_time:.2f} secondes", emoji="⏱️")
        
        # Analyser le résultat
        action = decision.get("action", "unknown")
        if action == "continuer":
            campagne_cible = decision.get("campagne_cible", "non spécifiée")
            self._pretty_log(f"DÉCISION: Continuer la campagne '{campagne_cible}'", emoji="🔄", color=Fore.GREEN)
        elif action == "nouvelle":
            self._pretty_log(f"DÉCISION: Démarrer une nouvelle campagne", emoji="🆕", color=Fore.GREEN)
        else:
            self._pretty_log(f"DÉCISION: Action inconnue '{action}'", emoji="❓", color=Fore.YELLOW)
        
        # Afficher le raisonnement
        self._pretty_log("Processus décisionnel:", emoji="🔍")
        decision_process = decision.get("decision_process", [])
        for i, step in enumerate(decision_process):
            self._pretty_log(f"  {i+1}. {step}", emoji="🧩")
        
        # Afficher les agents à impliquer
        agents = decision.get("agents_à_impliquer", [])
        self._pretty_log(f"Agents à impliquer dans l'exécution:", emoji="👥")
        for agent in agents:
            self._pretty_log(f"  → {agent}", emoji="🤖")
        
        # Enregistrer cette décision dans l'historique
        self.decision_history.append({
            "timestamp": datetime.datetime.now().isoformat(),
            "action": action,
            "target": decision.get("campagne_cible", None),
            "reasoning": decision.get("decision_process", []),
            "comment": decision.get("commentaire", "")
        })
        
        # Appeler les agents identifiés dans la décision, selon une chaîne de dépendance
        if decision and "agents_à_impliquer" in decision and len(decision.get("agents_à_impliquer", [])) > 0:
            self._pretty_log("Démarrage des agents subordonnés...", emoji="🚀", color=Fore.YELLOW)
            
            # Définir l'ordre de dépendance des agents
            dependency_chain = {
                "StrategyAgent": [],  # Aucune dépendance
                "PlanningAgent": ["StrategyAgent"],  # Dépend de StrategyAgent
                "CampaignStarterAgent": ["StrategyAgent", "PlanningAgent"],  # Dépend de StrategyAgent et PlanningAgent
                "ScraperAgent": ["CampaignStarterAgent"],  # Dépend de CampaignStarterAgent
                "CleanerAgent": ["ScraperAgent"],  # Dépend de ScraperAgent
                "ClassifierAgent": ["CleanerAgent"]  # Dépend de CleanerAgent
            }
            
            # Garder trace des agents qui ont réussi
            successful_agents = set()
            chain_broken = False
            
            for agent_name in decision.get("agents_à_impliquer", []):
                # Vérifier si toutes les dépendances ont réussi
                dependencies = dependency_chain.get(agent_name, [])
                missing_dependencies = [dep for dep in dependencies if dep not in successful_agents]
                
                if missing_dependencies or chain_broken:
                    chain_broken = True
                    self._pretty_log(f"Agent {agent_name} ignoré: chaîne d'exécution interrompue par des dépendances échouées: {missing_dependencies}", 
                                    emoji="⏭️", color=Fore.YELLOW)
                    agent_results[agent_name] = {"error": "Dépendances non satisfaites", "status": "SKIPPED"}
                    continue
                
                try:
                    # Tenter d'appeler l'agent
                    agent_result = self._call_agent(agent_name, decision, agent_results)
                    agent_results[agent_name] = agent_result
                    
                    # Vérifier si l'agent a échoué explicitement
                    if isinstance(agent_result, dict) and agent_result.get("status") == "FAILED":
                        error_message = agent_result.get('error', 'Raison inconnue')
                        self._pretty_log(f"Agent {agent_name} a échoué: {error_message}", 
                                        emoji="❌", color=Fore.RED)
                        
                        # Appeler le DebuggerAgent pour analyser et potentiellement résoudre l'erreur
                        debug_result = self._handle_agent_failure(agent_name, error_message, agent_result, agent_results, decision)
                        
                        # Si le DebuggerAgent a résolu le problème
                        if debug_result.get("resolution_action") == "AUTO_RESOLVE" and debug_result.get("auto_resolve_result", {}).get("success"):
                            self._pretty_log(f"DebuggerAgent a résolu le problème: {debug_result.get('auto_resolve_result', {}).get('details')}", 
                                           emoji="🔧", color=Fore.GREEN)
                            
                            # Si la résolution a fourni un nouveau résultat, utiliser ce résultat
                            retry_result = debug_result.get("auto_resolve_result", {}).get("retry_result")
                            if retry_result:
                                agent_results[agent_name] = retry_result
                                self._pretty_log(f"Agent {agent_name} réexécuté avec succès", emoji="✓", color=Fore.GREEN)
                                successful_agents.add(agent_name)
                                continue  # Passer à l'agent suivant, celui-ci est maintenant considéré comme réussi
                            
                        else:
                            # Si le DebuggerAgent n'a pas pu résoudre le problème
                            self._pretty_log(f"Problème non résolu: {debug_result.get('diagnostic', {}).get('summary')}", 
                                           emoji="⚠️", color=Fore.YELLOW)
                            
                            if debug_result.get("requires_human", False):
                                self._pretty_log("Intervention humaine requise", emoji="👤", color=Fore.MAGENTA)
                                
                            chain_broken = True
                            
                    elif "error" in agent_result and not agent_result.get("status") == "COMPLETED":
                        self._pretty_log(f"Agent {agent_name} a signalé une erreur: {agent_result.get('error')}", 
                                        emoji="⚠️", color=Fore.YELLOW)
                        chain_broken = True
                    else:
                        self._pretty_log(f"Agent {agent_name} exécuté avec succès", emoji="✓", color=Fore.GREEN)
                        successful_agents.add(agent_name)
                except Exception as e:
                    error_msg = str(e)
                    self._pretty_log(f"Erreur lors de l'appel à l'agent {agent_name}: {error_msg}", 
                                    emoji="❌", color=Fore.RED, level="ERROR")
                    agent_results[agent_name] = {"error": error_msg, "status": "ERROR"}
                    chain_broken = True
        
        # Mesurer le temps total d'exécution
        execution_time = time.time() - start_time
        self._pretty_log(f"Exécution terminée en {execution_time:.2f} secondes", emoji="✅", color=Fore.GREEN)
        self._pretty_log("==========================================", emoji="🧠", color=Fore.MAGENTA)
        
        # Construire et enrichir le résultat
        result = {
            "decision": decision,
            "thinking_steps": self.thinking_steps,
            "execution_time": execution_time,
            "timestamp": datetime.datetime.now().isoformat(),
            "brain_log_file": brain_log_file,
            "agent_results": agent_results
        }
        
        # Logger l'exécution de l'agent
        log_agent(self.name, input_data, result)
        
        return result
        
    def _call_agent(self, agent_name: str, decision: dict, agent_results: dict) -> dict:
        """
        Appelle un agent subordonné et retourne son résultat
        
        Args:
            agent_name: Nom de l'agent à appeler (ex: 'StrategyAgent')
            decision: Décision du DecisionBrainAgent contenant le contexte
            agent_results: Résultats des agents précédents dans la chaîne
            
        Returns:
            dict: Résultat de l'exécution de l'agent
        """
        self._pretty_log(f"Appel de l'agent {agent_name}...", emoji="📞")
        
        try:
            # Préparer les paramètres pour l'agent
            agent_params = self._prepare_agent_params(agent_name, decision, agent_results)
            
            # Importer dynamiquement l'agent
            if agent_name == "StrategyAgent":
                from agents.controller.strategy_agent import StrategyAgent
                agent = StrategyAgent()
            elif agent_name == "PlanningAgent":
                from agents.controller.planning_agent import PlanningAgent
                agent = PlanningAgent()
            elif agent_name == "CampaignStarterAgent":
                from agents.controller.campaign_starter_agent import CampaignStarterAgent
                agent = CampaignStarterAgent()
            elif agent_name == "ScraperAgent":
                # La classe s'appelle ApifyScraper, pas ScraperAgent
                from agents.scraper.apify_scraper import ApifyScraper
                agent = ApifyScraper()
            elif agent_name == "CleanerAgent":
                from agents.cleaner.lead_cleaner import CleanerAgent
                agent = CleanerAgent()
            elif agent_name == "ClassifierAgent" or agent_name == "LeadClassifierAgent":
                from agents.classifier.lead_classifier_agent import LeadClassifierAgent
                agent = LeadClassifierAgent()
            elif agent_name == "AnalyticsAgent":
                from agents.analytics.analytics_agent import AnalyticsAgent
                agent = AnalyticsAgent()
            else:
                raise ValueError(f"Agent non reconnu: {agent_name}")
            
            # Exécuter l'agent
            result = agent.run(agent_params)
            return result
        except ImportError as e:
            self._pretty_log(f"Impossible d'importer l'agent {agent_name}: {str(e)}", emoji="❌", level="ERROR")
            return {"error": f"Import error: {str(e)}"}
        except Exception as e:
            self._pretty_log(f"Erreur lors de l'exécution de l'agent {agent_name}: {str(e)}", emoji="❌", level="ERROR")
            return {"error": str(e)}
    
    def _handle_agent_failure(self, failed_agent: str, error_message: str, agent_result: dict, agent_results: dict, decision: dict) -> dict:
        """
        Gère l'échec d'un agent en appelant le DebuggerAgent pour analyser et potentiellement résoudre le problème
        
        Args:
            failed_agent: Nom de l'agent qui a échoué
            error_message: Message d'erreur
            agent_result: Résultat complet de l'agent qui a échoué
            agent_results: Résultats de tous les agents exécutés jusqu'à présent
            decision: Décision du DecisionBrainAgent
            
        Returns:
            dict: Résultat de l'analyse du DebuggerAgent
        """
        self._pretty_log(f"Appel du DebuggerAgent pour analyser l'erreur de {failed_agent}...", emoji="🔍", color=Fore.YELLOW)
        
        try:
            # Importer et instancier le DebuggerAgent
            from agents.controller.debugger_agent import DebuggerAgent
            debugger = DebuggerAgent()
            
            # Préparer les données pour le DebuggerAgent
            debug_input = {
                "failed_agent": failed_agent,
                "error_message": error_message,
                "error_status": agent_result.get("status", "FAILED"),
                "agent_results": agent_results,
                "brain_decision": decision,
                "context": {
                    "timestamp": datetime.datetime.now().isoformat(),
                    "initiated_by": "DecisionBrainAgent"
                }
            }
            
            # Exécuter le DebuggerAgent
            debug_result = debugger.run(debug_input)
            
            # Logging du résultat
            self._pretty_log(f"Analyse du problème: {debug_result.get('diagnostic', {}).get('summary', 'Non disponible')}", 
                           emoji="📋", color=Fore.YELLOW)
            
            return debug_result
            
        except ImportError as e:
            self._pretty_log(f"Impossible d'importer le DebuggerAgent: {str(e)}", emoji="❌", level="ERROR")
            # Retourner un résultat par défaut
            return {
                "status": "ERROR",
                "resolution_action": "NOTIFY_ADMIN",
                "resolution_details": f"Erreur lors de l'importation du DebuggerAgent: {str(e)}",
                "requires_human": True
            }
        except Exception as e:
            self._pretty_log(f"Erreur lors de l'exécution du DebuggerAgent: {str(e)}", emoji="❌", level="ERROR")
            # Retourner un résultat par défaut
            return {
                "status": "ERROR",
                "resolution_action": "NOTIFY_ADMIN",
                "resolution_details": f"Erreur lors de l'exécution du DebuggerAgent: {str(e)}",
                "requires_human": True
            }
    
    def _prepare_agent_params(self, agent_name: str, decision: dict, agent_results: dict) -> dict:
        """
        Prépare les paramètres à passer à un agent en fonction de son type
        
        Args:
            agent_name: Nom de l'agent
            decision: Décision du DecisionBrainAgent
            agent_results: Résultats des agents précédents
            
        Returns:
            dict: Paramètres pour l'agent
        """
        # Paramètres communs
        params = {
            "initiated_by": "DecisionBrainAgent",
            "brain_decision": decision
        }
        
        # Paramètres spécifiques par type d'agent
        if agent_name == "StrategyAgent":
            params["approach"] = "initial" if decision.get("action") == "nouvelle" else "optimization"
        
        elif agent_name == "PlanningAgent":
            # Pour PlanningAgent on transmet la décision du cerveau
            if decision.get("action") == "nouvelle":
                params["operation"] = "plan_new_campaign"
            else:
                params["operation"] = "plan_continuation"
                params["campaign_id"] = decision.get("campagne_cible")
        
        elif agent_name == "CampaignStarterAgent":
            # Configuration minimale pour un démarrage initial
            if decision.get("action") == "nouvelle":
                params["operation"] = "start_new_campaign"
                
                # Récupérer la niche du StrategyAgent si elle existe
                if "StrategyAgent" in agent_results and agent_results["StrategyAgent"].get("niche"):
                    # Convertir en dictionnaire comme attendu par CampaignStarterAgent
                    niche_value = agent_results["StrategyAgent"]["niche"]
                    params["validated_niche"] = {"niche": niche_value, "source": "StrategyAgent"}
                    self._pretty_log(f"Niche validée obtenue du StrategyAgent: {niche_value}", emoji="🔗", color=Fore.GREEN)
                else:
                    # Utiliser une niche par défaut au format dictionnaire
                    params["validated_niche"] = {"niche": "Avocats", "source": "Default"}
                    self._pretty_log("Utilisation d'une niche par défaut: Avocats", emoji="⚠️", color=Fore.YELLOW)
            else:
                params["operation"] = "continue_campaign" 
                params["campaign_id"] = decision.get("campagne_cible")
        
        # Pour les autres agents, utiliser les paramètres génériques
        
        return params
