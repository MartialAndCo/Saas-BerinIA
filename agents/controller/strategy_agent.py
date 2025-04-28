from agents.base.base import AgentBase
from db.postgres import get_campaign_summary, PostgresClient
from utils.llm import ask_gpt_4_1
from memory.qdrant import QdrantClient, get_campaign_knowledge
from logs.agent_logger import log_agent
import json
import datetime
import os

class StrategyAgent(AgentBase):
    def __init__(self):
        super().__init__("StrategyAgent")
        self.db_client = PostgresClient()
        self.qdrant_client = QdrantClient()
        self.rejected_niches_memory_file = "logs/rejected_niches.json"
        self._ensure_rejected_niches_file_exists()

    def _ensure_rejected_niches_file_exists(self):
        """Ensures that the rejected niches file exists"""
        if not os.path.exists(self.rejected_niches_memory_file):
            with open(self.rejected_niches_memory_file, "w") as f:
                json.dump({"rejected_niches": [], "last_updated": datetime.datetime.now().isoformat()}, f)

    def _get_rejected_niches(self):
        """Get the list of niches that were rejected by the PlanningAgent"""
        try:
            with open(self.rejected_niches_memory_file, "r") as f:
                data = json.load(f)
                return data.get("rejected_niches", [])
        except Exception as e:
            print(f"[{self.name}] ⚠️ Erreur lors de la récupération des niches rejetées: {str(e)}")
            return []

    def _add_rejected_niche(self, niche, reason):
        """Add a niche to the rejected niches list with timestamp and reason"""
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
                
            # Save to PostgreSQL (simulation for now)
            self._store_strategy_decision_in_db(niche, "REJECTED", reason)
            
            return True
        except Exception as e:
            print(f"[{self.name}] ⚠️ Erreur lors de l'ajout d'une niche rejetée: {str(e)}")
            return False

    def _store_strategy_decision_in_db(self, niche, decision_type, reason):
        """Store strategy decision in PostgreSQL for auditing and analysis"""
        try:
            # In a real implementation, this would execute an SQL INSERT query
            print(f"[{self.name}] 📊 Décision stratégique enregistrée en base pour audit: {niche} - {decision_type}")
            
            # Log the decision to a file for easier auditing
            decision_log = {
                "timestamp": datetime.datetime.now().isoformat(),
                "niche": niche,
                "decision_type": decision_type,
                "reason": reason,
                "agent": self.name
            }
            
            with open(f"logs/strategy_decisions_{datetime.datetime.now().strftime('%Y%m%d')}.json", "a") as f:
                f.write(json.dumps(decision_log) + "\n")
                
            return True
        except Exception as e:
            print(f"[{self.name}] ⚠️ Erreur lors de l'enregistrement de la décision: {str(e)}")
            return False

    def _get_similar_successful_niches(self, successful_niches, limit=3):
        """
        Generate similar niches based on successful ones
        For example: If "Plombiers à Paris" works well, suggest "Plombiers à Lyon"
        """
        if not successful_niches:
            return []
            
        # Prepare a prompt to generate similar niches
        prompt = f"""
        Voici une liste de niches qui ont bien fonctionné : {', '.join(successful_niches)}.
        
        Génère {limit} nouvelles niches similaires à celles-ci, en variant par exemple:
        - La localisation géographique (Paris → Lyon, Bordeaux, etc.)
        - Le secteur précis (Plombiers → Électriciens, Chauffagistes, etc.)
        - La spécialisation (Avocats généralistes → Avocats spécialisés en droit des affaires)
        
        Ne propose pas de niches identiques à celles de la liste d'origine.
        
        Format attendu :
        - similar_niches: [liste de {limit} niches similaires]
        - similarity_explanation: [explication pour chaque niche de comment elle est similaire]
        """
        
        response_text = ask_gpt_4_1(prompt)
        
        # Traitement du résultat
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
                
            return response.get("similar_niches", [])
            
        except json.JSONDecodeError as e:
            print(f"[{self.name}] ⚠️ Erreur lors du parsing de la réponse JSON pour les niches similaires: {str(e)}")
            print(f"[{self.name}] Réponse brute: {response_text[:200]}...")
            return []
        except Exception as e:
            print(f"[{self.name}] ⚠️ Erreur lors du traitement des niches similaires: {str(e)}")
            return []

    def _query_unexplored_domains(self):
        """
        Query Qdrant for potential domains that haven't been explored yet but match our criteria
        """
        # In a real implementation, this would use vector similarity search
        # For now, we'll simulate with a prompt to generate unexplored domains
        
        prompt = """
        En tant qu'expert en prospection B2B pour des solutions d'IA (chatbots, standards téléphoniques IA), 
        suggère 3 domaines d'activité qui n'ont probablement pas encore été explorés par notre entreprise,
        mais qui présentent un potentiel élevé pour nos solutions.
        
        Ces domaines doivent:
        - Être des TPE/PME ou indépendants
        - Avoir un besoin évident de disponibilité téléphonique ou chat
        - Ne pas être des commerces grand public
        
        Format attendu:
        - unexplored_domains: [liste de 3 domaines]
        - potential_explanation: [explication du potentiel pour chaque domaine]
        """
        
        response_text = ask_gpt_4_1(prompt)
        
        # Traitement du résultat
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
                
            return response.get("unexplored_domains", [])
            
        except json.JSONDecodeError as e:
            print(f"[{self.name}] ⚠️ Erreur lors du parsing de la réponse JSON pour les domaines inexplorés: {str(e)}")
            print(f"[{self.name}] Réponse brute: {response_text[:200]}...")
            return []
        except Exception as e:
            print(f"[{self.name}] ⚠️ Erreur lors du traitement des domaines inexplorés: {str(e)}")
            return []

    def run(self, input_data: dict = {}) -> dict:
        print(f"[{self.name}] 🔍 Recherche stratégique d'une nouvelle niche...")

        # Get campaign summary and rejected niches
        past_niches = get_campaign_summary()
        rejected_niches = self._get_rejected_niches()
        
        # Determine the strategy approach based on input or randomly select one
        approach = input_data.get("approach", "standard")
        
        if approach == "similarity":
            # Use similarity-based generation if successful niches exist
            successful_niches = past_niches.get("top_performing_niches", [])
            similar_niches = self._get_similar_successful_niches(successful_niches)
            similar_niches_str = ", ".join(similar_niches)
            approach_context = f"Considère en priorité ces niches similaires à celles qui ont déjà réussi: {similar_niches_str}"
        elif approach == "unexplored":
            # Query for unexplored domains with potential
            unexplored_domains = self._query_unexplored_domains()
            unexplored_str = ", ".join(unexplored_domains)
            approach_context = f"Considère en priorité ces domaines peu explorés mais à fort potentiel: {unexplored_str}"
        else:
            approach_context = "Trouve une nouvelle niche originale à explorer."

        # Get rejected niches formatted as a string
        rejected_niches_list = [entry["niche"] for entry in rejected_niches]
        rejected_niches_with_reasons = [f"{entry['niche']} (motif: {entry['reason']})" for entry in rejected_niches]
        rejected_niches_str = "\n".join(rejected_niches_with_reasons) if rejected_niches_with_reasons else "Aucune niche récemment rejetée."

        prompt = f"""
Tu es un agent stratégique chez BerinIA, une entreprise spécialisée dans l'installation de solutions d'IA pour les entreprises.

🎯 Ce que nous proposons :
- Installation de **chatbots intelligents** sur les sites web pour répondre aux questions, informer, guider, convertir.
- Mise en place de **standards téléphoniques IA** pour ne plus perdre d'appels : l'IA répond, qualifie, redirige ou prend un RDV.

👥 Nos cibles :
- Nous travaillons exclusivement en **B2B**.
- Nous visons des **TPE/PME ou indépendants**, notamment ceux qui perdent des clients à cause :
  - d'un manque de disponibilité au téléphone
  - de l'absence de réponses sur leur site
  - d'un besoin d'automatiser une partie du service client

🚫 Ne propose jamais :
- De niches grand public (supermarchés, centres commerciaux, associations, grandes chaînes de distribution)
- De niches déjà testées récemment ou sans pertinence pour notre service
- De niches récemment rejetées par l'équipe de planification

✅ Ce que tu dois faire :
- Proposer **une niche d'activité professionnelle spécifique** (ex. : "salons de massage", "plombiers", "cabinets dentaires")
- Cette niche doit avoir un **besoin évident** de présence téléphonique ou de chatbot
- Elle doit être **logique avec notre offre**, et ne pas déjà avoir été testée

{approach_context}

🧾 Voici les niches déjà testées :
{json.dumps(past_niches, indent=2)}

📋 Voici les niches récemment rejetées par l'équipe de planification :
{rejected_niches_str}

🔁 Ne propose rien de redondant ou trop proche s'il n'y a pas de vraie différence dans le besoin.

Donne-moi :
- Une seule niche, précise
- Une justification stratégique et logique
- Une estimation du potentiel de conversion (faible, moyen, élevé)
- Des suggestions de message adaptés à cette niche pour le premier contact

Format attendu (strict) :
- niche: <nom>
- justification: <texte>
- potentiel_conversion: <faible|moyen|élevé>
- suggestions_message: <liste>
"""

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
            
            # Utiliser une réponse par défaut en cas d'erreur
            response = {
                "niche": "Cabinets d'avocats spécialisés",
                "justification": "Valeur par défaut suite à une erreur de parsing. Les cabinets d'avocats ont un fort besoin de disponibilité et de qualifications des appels.",
                "potentiel_conversion": "élevé",
                "suggestions_message": [
                    "Combien d'appels manqués estimez-vous par semaine?",
                    "Notre standard IA peut filtrer vos appels selon vos critères précis."
                ]
            }
        except Exception as e:
            print(f"[{self.name}] ⚠️ Erreur lors du traitement de la réponse: {str(e)}")
            
            # Utiliser une réponse par défaut en cas d'erreur
            response = {
                "niche": "Agences immobilières indépendantes",
                "justification": "Valeur par défaut suite à une erreur. Les agences immobilières ont un fort besoin de disponibilité pour les premiers contacts clients.",
                "potentiel_conversion": "moyen",
                "suggestions_message": [
                    "Ne perdez plus jamais un acheteur potentiel à cause d'un appel manqué",
                    "Notre solution peut qualifier vos prospects immobiliers 24/7"
                ]
            }
        
        # Store the decision for auditing
        niche = response.get("niche")
        justification = response.get("justification")
        self._store_strategy_decision_in_db(niche, "PROPOSED", justification)
        
        # Enrich the result with additional context
        result = {
            "niche": niche,
            "justification": justification,
            "potentiel_conversion": response.get("potentiel_conversion", "moyen"),
            "suggestions_message": response.get("suggestions_message", []),
            "approach_used": approach,
            "prompt_used": prompt,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        # Log the agent's activity
        log_agent(self.name, input_data, result)
        
        return result
