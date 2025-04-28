from agents.base.base import AgentBase
from db.postgres import is_niche_already_scheduled
from utils.llm import ask_gpt_4_1
from logs.agent_logger import log_agent
import datetime
import json
import os

class PlanningAgent(AgentBase):
    def __init__(self):
        super().__init__("PlanningAgent")
        self.prompt_path = "prompts/planning_agent_prompt.txt"
        self.rejected_niches_memory_file = "logs/rejected_niches.json"
        self._ensure_rejected_niches_file_exists()

    def _ensure_rejected_niches_file_exists(self):
        """Ensures that the rejected niches file exists"""
        if not os.path.exists(self.rejected_niches_memory_file):
            with open(self.rejected_niches_memory_file, "w") as f:
                json.dump({"rejected_niches": [], "last_updated": datetime.datetime.now().isoformat()}, f)

    def _register_rejected_niche(self, niche, reason):
        """
        Register a rejected niche so that the StrategyAgent won't propose it again soon
        """
        try:
            with open(self.rejected_niches_memory_file, "r") as f:
                data = json.load(f)
            
            # Add the new rejected niche with metadata
            data["rejected_niches"].append({
                "niche": niche,
                "reason": reason,
                "timestamp": datetime.datetime.now().isoformat(),
                "cooldown_days": 30  # Default cooldown period before reproposing
            })
            
            # Update last_updated timestamp
            data["last_updated"] = datetime.datetime.now().isoformat()
            
            with open(self.rejected_niches_memory_file, "w") as f:
                json.dump(data, f, indent=2)
                
            print(f"[{self.name}] 📝 Niche '{niche}' rejetée et enregistrée dans la mémoire partagée.")
            return True
        except Exception as e:
            print(f"[{self.name}] ⚠️ Erreur lors de l'enregistrement de la niche rejetée: {str(e)}")
            return False

    def run(self, input_data: dict) -> dict:
        # Vérifier et gérer les valeurs None pour éviter les erreurs
        niche = input_data.get("niche") or "non spécifiée"
        justification = input_data.get("justification") or "Pas de justification fournie"
        potentiel_conversion = input_data.get("potentiel_conversion") or "moyen"
        
        # Vérifier si la niche vient du StrategyAgent via brain_decision
        if "brain_decision" in input_data and "agent_results" in input_data.get("brain_decision", {}):
            strategy_result = input_data["brain_decision"].get("agent_results", {}).get("StrategyAgent", {})
            if strategy_result and "niche" in strategy_result:
                niche = strategy_result["niche"]
                justification = strategy_result.get("justification", justification)
                potentiel_conversion = strategy_result.get("potentiel_conversion", potentiel_conversion)
        
        print(f"[{self.name}] 🗓️ Évaluation de la planification pour la niche : {niche}")

        # Vérification de doublons
        if is_niche_already_scheduled(niche):
            reason = "Déjà en cours ou récemment testée"
            # Register this rejection in the shared memory
            self._register_rejected_niche(niche, reason)
            
            result = {
                "planned": False,
                "reason": reason,
                "timestamp": datetime.datetime.now().isoformat(),
                "niche": niche
            }
            log_agent(self.name, input_data, result)
            return result

        # Charger le prompt depuis le fichier
        try:
            with open(self.prompt_path, "r") as file:
                prompt_template = file.read()
        except Exception as e:
            result = {
                "planned": False,
                "reason": f"Erreur lors du chargement du prompt: {str(e)}",
                "timestamp": datetime.datetime.now().isoformat(),
                "niche": niche
            }
            log_agent(self.name, input_data, result)
            return result

        # Construire le prompt avec les données contextuelles
        # Assurer que toutes les valeurs sont des chaînes pour éviter les erreurs de replace()
        prompt = prompt_template.replace("{{niche}}", str(niche))
        prompt = prompt.replace("{{justification}}", str(justification))
        prompt = prompt.replace("{{potentiel_conversion}}", str(potentiel_conversion))
        prompt = prompt.replace("{{current_date}}", datetime.datetime.now().strftime("%Y-%m-%d"))
        
        # Ajouter le contexte des campagnes actives si disponible
        active_campaigns_context = input_data.get("active_campaigns_context", "Information non disponible")
        prompt = prompt.replace("{{active_campaigns_context}}", active_campaigns_context)

        # Appeler GPT-4.1 pour la décision
        response_text = ask_gpt_4_1(prompt)
        
        # Traiter la réponse
        try:
            # Si la réponse est une chaîne, tenter de la convertir en objet JSON
            if isinstance(response_text, str):
                if "```json" in response_text:
                    json_start = response_text.find("```json") + 7
                    json_end = response_text.find("```", json_start)
                    if json_end > json_start:
                        response_text = response_text[json_start:json_end].strip()
                elif "```" in response_text:
                    json_start = response_text.find("```") + 3
                    json_end = response_text.find("```", json_start)
                    if json_end > json_start:
                        response_text = response_text[json_start:json_end].strip()
                
                # Parser le JSON
                response = json.loads(response_text)
            else:
                # Si c'est déjà un dictionnaire, l'utiliser directement
                response = response_text
        except json.JSONDecodeError as e:
            print(f"[{self.name}] ⚠️ Erreur lors du parsing de la réponse JSON: {str(e)}")
            print(f"[{self.name}] Réponse brute: {response_text[:200]}...")
            
            # Réponse par défaut en cas d'erreur de parsing
            response = {
                "planned": True,  # Par défaut, on accepte la niche
                "messages": [
                    "Nos standards IA sont parfaits pour votre secteur!", 
                    "Ne perdez plus un seul appel client!", 
                    "Qualifiez vos leads 24/7 avec notre IA"
                ],
                "target_campaign_start": (datetime.datetime.now() + datetime.timedelta(days=3)).strftime("%Y-%m-%d"),
                "resources_required": {
                    "storage_mb": 100,
                    "leads_quota": 1000,
                    "expected_cost": 350
                },
                "reason": "Par défaut suite à une erreur de parsing",
                "priority": "medium"
            }
        except Exception as e:
            print(f"[{self.name}] ⚠️ Erreur lors du traitement de la réponse: {str(e)}")
            
            # Réponse par défaut en cas d'autre erreur
            response = {
                "planned": True,
                "reason": "Erreur de traitement, planning par défaut",
                "priority": "low"
            }
        
        # Si la niche est rejetée, l'enregistrer
        if response.get("planned") is False:
            reason = response.get("reason", "Raison non spécifiée")
            self._register_rejected_niche(niche, reason)
        
        # Enrichir la réponse
        response["timestamp"] = datetime.datetime.now().isoformat()
        response["niche"] = niche
        
        # Enregistrer les logs
        log_agent(self.name, input_data, response)
        
        return response
