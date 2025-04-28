from agents.base.base import AgentBase
from utils.llm import ask_gpt_4_1
from logs.agent_logger import log_agent
import json
import datetime

class PivotAgent(AgentBase):
    def __init__(self):
        super().__init__("PivotAgent")
        self.prompt_path = "prompts/pivot_agent_prompt.txt"

    def run(self, input_data: dict) -> dict:
        print(f"[{self.name}] 🔄 Analyse des résultats pour décision stratégique (pivot/continuer/dupliquer)...")
        
        # Récupérer les données d'analyse
        campaign_data = input_data.get("campaign_data", {})
        analytics_results = input_data.get("analytics_results", {})
        messenger_feedback = input_data.get("messenger_feedback", {})  # Nouveau: feedback du MessengerAgent
        duplication_options = input_data.get("duplication_options", False)  # Nouveau: activer l'option de duplication intelligente
        
        if not analytics_results:
            result = {"error": "Aucun résultat d'analyse fourni", "decision": "ERROR"}
            log_agent(self.name, input_data, result)
            return result
        
        # Charger le prompt depuis le fichier
        try:
            with open(self.prompt_path, "r") as file:
                prompt_template = file.read()
        except Exception as e:
            result = {"error": f"Erreur lors du chargement du prompt: {str(e)}", "decision": "ERROR"}
            log_agent(self.name, input_data, result)
            return result
        
        # Enrichir les données de campagne avec les données de performance des messages
        if messenger_feedback:
            if "metrics" not in campaign_data:
                campaign_data["metrics"] = {}
            campaign_data["metrics"]["messenger_feedback"] = messenger_feedback
        
        # Construire le prompt avec les données
        prompt = prompt_template
        prompt = prompt.replace("{{campaign_data}}", json.dumps(campaign_data, ensure_ascii=False))
        prompt = prompt.replace("{{analytics_results}}", json.dumps(analytics_results, ensure_ascii=False))
        prompt = prompt.replace("{{current_date}}", datetime.datetime.now().strftime("%Y-%m-%d"))
        
        # Ajouter les données du MessengerAgent au prompt
        if messenger_feedback:
            prompt = prompt.replace("{{messenger_feedback}}", json.dumps(messenger_feedback, ensure_ascii=False))
        else:
            prompt = prompt.replace("{{messenger_feedback}}", "{}")
        
        # Spécifier si l'option de duplication intelligente est activée
        prompt = prompt.replace("{{duplication_options}}", "true" if duplication_options else "false")
        
        # Appeler GPT-4.1 pour la décision
        response = ask_gpt_4_1(prompt)
        
        # Enrichir la réponse
        response["timestamp"] = datetime.datetime.now().isoformat()
        response["campaign_id"] = campaign_data.get("campaign_id", "unknown")
        
        # Vérifier le format de la réponse
        if "decision" not in response:
            response["error"] = "Format de réponse incorrect"
            response["decision"] = "ERROR"
        
        # Enregistrer les logs
        log_agent(self.name, input_data, response)
        
        # Déclencher des actions en fonction de la décision
        if response.get("decision") == "PIVOT":
            self._register_pivot_decision(campaign_data, response)
        elif response.get("decision") == "DUPLICATE":
            self._register_duplication_decision(campaign_data, response)
        elif response.get("decision") == "CONTINUE":
            self._register_continuation_decision(campaign_data, response)
        
        return response
    
    def _register_pivot_decision(self, campaign_data, decision):
        """
        Enregistre la décision de pivoter pour une campagne
        """
        campaign_id = campaign_data.get("campaign_id", "unknown")
        print(f"[{self.name}] Décision de PIVOT enregistrée pour la campagne {campaign_id}")
        print(f"[{self.name}] Raison: {decision.get('justification', 'Non spécifiée')}")
        
        # Détails du pivot
        pivot_details = decision.get("pivot_details", {})
        if pivot_details:
            print(f"[{self.name}] Détails du pivot:")
            print(f"  - Nouvelle niche: {pivot_details.get('new_niche', 'Non spécifiée')}")
            print(f"  - Nouvelles cibles: {pivot_details.get('new_targets', 'Non spécifiées')}")
            print(f"  - Changements de message: {pivot_details.get('message_changes', 'Non spécifiés')}")
        
        # Dans une implémentation réelle, on pourrait enregistrer cela en BDD
        
    def _register_duplication_decision(self, campaign_data, decision):
        """
        Enregistre la décision de dupliquer une campagne avec variations
        """
        campaign_id = campaign_data.get("campaign_id", "unknown")
        print(f"[{self.name}] Décision de DUPLICATION enregistrée pour la campagne {campaign_id}")
        
        # Nouvelles cibles
        target_niches = decision.get("target_niches", [])
        if target_niches:
            print(f"[{self.name}] Nouvelles cibles: {', '.join(target_niches)}")
        
        # Variations de messages
        message_variations = decision.get("message_variations", [])
        if message_variations:
            print(f"[{self.name}] Variations de messages à tester:")
            for i, variation in enumerate(message_variations):
                print(f"  {i+1}. {variation.get('description', 'Variation')} - {variation.get('expected_impact', 'Impact non spécifié')}")
        
        # Variations de ciblage
        targeting_variations = decision.get("targeting_variations", [])
        if targeting_variations:
            print(f"[{self.name}] Variations de ciblage à tester:")
            for i, variation in enumerate(targeting_variations):
                print(f"  {i+1}. {variation.get('description', 'Variation')} - {variation.get('expected_impact', 'Impact non spécifié')}")
        
        # Dans une implémentation réelle, on pourrait créer les campagnes dupliquées avec les variations
        
    def _register_continuation_decision(self, campaign_data, decision):
        """
        Enregistre la décision de continuer une campagne
        """
        campaign_id = campaign_data.get("campaign_id", "unknown")
        print(f"[{self.name}] Décision de CONTINUATION enregistrée pour la campagne {campaign_id}")
        
        # Ajustements suggérés
        adjustments = decision.get("adjustments", [])
        if adjustments:
            print(f"[{self.name}] Ajustements suggérés:")
            for i, adjustment in enumerate(adjustments):
                print(f"  {i+1}. {adjustment}")
        
        # Optimisations de message
        message_optimizations = decision.get("message_optimizations", [])
        if message_optimizations:
            print(f"[{self.name}] Optimisations de message recommandées:")
            for i, optimization in enumerate(message_optimizations):
                print(f"  {i+1}. {optimization.get('description', 'Optimisation')} - {optimization.get('expected_impact', 'Impact non spécifié')}")
        
        # Dans une implémentation réelle, on pourrait appliquer les ajustements suggérés
