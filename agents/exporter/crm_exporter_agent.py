from agents.base.base import AgentBase
from utils.llm import ask_gpt_4_1
from logs.agent_logger import log_agent
from logs.enhanced_logger import get_agent_logger
import datetime
import logging
import os
import json

# Importer le connecteur Berinia
try:
    from integrations.berinia.db_connector import (
        export_leads_to_berinia, 
        create_campaign_in_berinia,
        get_all_campaigns,
        test_berinia_connection
    )
    BERINIA_AVAILABLE = True
    logging.info("✅ Module d'intégration Berinia disponible.")
except ImportError:
    BERINIA_AVAILABLE = False
    logging.error("❌ Module d'intégration Berinia non disponible. L'exportation ne fonctionnera pas.")

class CRMExporterAgent(AgentBase):
    def __init__(self):
        super().__init__("CRMExporterAgent")
        self.prompt_path = "prompts/crm_exporter_agent_prompt.txt"
        # Initialiser le logger amélioré
        self.enhanced_logger = get_agent_logger(self.name)

    def run(self, input_data: dict) -> dict:
        self.enhanced_logger.log_input(input_data)
        print(f"[{self.name}] 📤 Décision d'exportation des leads vers le CRM...")
        self.enhanced_logger.log_processing("Décision d'exportation des leads vers le CRM...")

        # Récupérer les leads classifiés
        classified_leads = input_data.get("classified_leads", [])
        
        if not classified_leads:
            result = {"error": "Aucun lead à exporter", "export_decision": {"leads_to_export_now": [], "leads_to_delay": []}}
            self.enhanced_logger.log_error("Aucun lead à exporter", {"input_data": "empty"})
            log_agent(self.name, input_data, result)
            self.enhanced_logger.log_output(result)
            self.enhanced_logger.log_completion("no_leads")
            return result

        # Récupérer des informations système pour la décision d'exportation
        # Ces informations pourraient venir d'une API CRM réelle dans une implémentation complète
        system_info = {
            "pending_leads_count": input_data.get("pending_leads_count", 15),
            "daily_limit": input_data.get("daily_limit", 50),
            "exported_today": input_data.get("exported_today", 25),
            "current_day": datetime.datetime.now().strftime("%A"),
            "current_time": datetime.datetime.now().strftime("%H:%M")
        }

        # Charger le prompt depuis le fichier
        try:
            with open(self.prompt_path, "r") as file:
                prompt_template = file.read()
            self.enhanced_logger.log_processing("Prompt chargé avec succès")
        except Exception as e:
            result = {"error": f"Erreur lors du chargement du prompt: {str(e)}", "export_decision": {"leads_to_export_now": [], "leads_to_delay": []}}
            self.enhanced_logger.log_error(e, {"step": "prompt_loading", "path": self.prompt_path})
            log_agent(self.name, input_data, result)
            self.enhanced_logger.log_output(result)
            self.enhanced_logger.log_completion("failure")
            return result

        # Construire le prompt avec les données
        prompt = prompt_template
        prompt = prompt.replace("{{classified_leads}}", json.dumps(classified_leads, ensure_ascii=False, indent=2))
        prompt = prompt.replace("{{pending_leads_count}}", str(system_info["pending_leads_count"]))
        prompt = prompt.replace("{{daily_limit}}", str(system_info["daily_limit"]))
        prompt = prompt.replace("{{exported_today}}", str(system_info["exported_today"]))
        prompt = prompt.replace("{{current_day}}", system_info["current_day"])
        prompt = prompt.replace("{{current_time}}", system_info["current_time"])
        self.enhanced_logger.log_processing("Prompt préparé avec les données contextuelles")

        # Appeler GPT-4.1 pour la décision d'exportation
        try:
            self.enhanced_logger.log_processing("Appel de GPT-4.1 pour la décision d'exportation")
            response_text = ask_gpt_4_1(prompt)
            print(f"[{self.name}] Réponse GPT-4.1 reçue, analyse en cours...")
            self.enhanced_logger.log_processing("Réponse GPT-4.1 reçue, analyse en cours...")
            
            # Convertir la réponse JSON en dictionnaire Python
            try:
                # Si la réponse contient des délimiteurs de code JSON, extraire uniquement le JSON
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
                
                response = json.loads(response_text)
                
                # Vérifier que la structure est conforme à ce qui est attendu
                if "export_decision" not in response:
                    print(f"[{self.name}] ⚠️ Structure de réponse non conforme, ajout de la structure manquante")
                    self.enhanced_logger.log_processing("⚠️ Structure de réponse non conforme, ajout de la structure manquante")
                    response["export_decision"] = {
                        "leads_to_export_now": [],
                        "leads_to_delay": []
                    }
                
                # S'assurer que leads_to_export_now existe
                if "leads_to_export_now" not in response["export_decision"]:
                    response["export_decision"]["leads_to_export_now"] = []
                
                # Forcer l'export de tous les leads WARM si aucun n'est sélectionné
                if not response["export_decision"]["leads_to_export_now"]:
                    warm_leads = [lead for lead in classified_leads 
                                if (isinstance(lead.get("classification"), dict) and 
                                    lead.get("classification", {}).get("qualite_lead") == "WARM") or
                                   lead.get("gpt_temperature") == "warm"]
                    
                    if warm_leads:
                        print(f"[{self.name}] 🔄 Ajout automatique de {len(warm_leads)} leads chauds non sélectionnés")
                        self.enhanced_logger.log_processing(f"🔄 Ajout automatique de {len(warm_leads)} leads chauds non sélectionnés")
                        for lead in warm_leads:
                            response["export_decision"]["leads_to_export_now"].append({
                                "id": lead.get("id", "unknown"),
                                "qualite": "WARM",
                                "raison_export": "Lead chaud ajouté automatiquement"
                            })
            
            except json.JSONDecodeError as je:
                print(f"[{self.name}] ❌ Erreur lors du décodage JSON: {str(je)}")
                print(f"[{self.name}] Réponse brute: {response_text[:200]}...")
                self.enhanced_logger.log_error(je, {"step": "json_parsing", "response_preview": response_text[:200]})
                
                # Créer une réponse par défaut
                response = {
                    "export_decision": {
                        "leads_to_export_now": [],
                        "leads_to_delay": []
                    },
                    "error": f"Erreur JSON: {str(je)}"
                }
                
                # Ajouter les leads chauds/tièdes par défaut
                warm_leads = [lead for lead in classified_leads 
                            if (isinstance(lead.get("classification"), dict) and 
                                lead.get("classification", {}).get("qualite_lead") in ["WARM", "HOT"]) or
                              lead.get("gpt_temperature") in ["warm", "hot"]]
                
                for lead in warm_leads[:10]:  # Limiter à 10 leads
                    response["export_decision"]["leads_to_export_now"].append({
                        "id": lead.get("id", "unknown"),
                        "qualite": lead.get("classification", {}).get("qualite_lead", "WARM"),
                        "raison_export": "Lead prioritaire (ajouté automatiquement après erreur)"
                    })
                    
                self.enhanced_logger.log_processing(f"Ajout automatique de {len(warm_leads[:10])} leads prioritaires après erreur JSON")
        except Exception as e:
            print(f"[{self.name}] ❌ Erreur lors de l'appel à GPT-4.1: {str(e)}")
            self.enhanced_logger.log_error(e, {"step": "gpt_call"})
            response = {
                "error": f"Erreur GPT-4.1: {str(e)}",
                "export_decision": {
                    "leads_to_export_now": [],
                    "leads_to_delay": []
                }
            }

        # Fonction pour réaliser l'exportation des leads sélectionnés
        self.enhanced_logger.log_processing("Début de l'exportation des leads sélectionnés")
        export_result = self._batch_export_leads(response, classified_leads)
        
        # Fusionner le résultat d'exportation avec la décision
        if isinstance(export_result, dict):
            response.update(export_result)
        
        # Enregistrer les logs
        log_agent(self.name, input_data, response)
        
        # Logs améliorés pour le résultat final
        if export_result.get("success", False):
            self.enhanced_logger.log_output(response)
            self.enhanced_logger.log_completion("success")
        else:
            self.enhanced_logger.log_output(response)
            self.enhanced_logger.log_completion("failure")
        
        return response
    
    def _batch_export_leads(self, export_decision, classified_leads):
        """
        Méthode auxiliaire pour l'exportation effective des leads vers la base de données Berinia.
        
        Args:
            export_decision: Décision d'exportation avec les leads à exporter
            classified_leads: Liste complète des leads classifiés
        """
        # Extraire les IDs des leads à exporter
        leads_to_export_ids = []
        try:
            for lead in export_decision.get("export_decision", {}).get("leads_to_export_now", []):
                if isinstance(lead, dict) and "id" in lead:
                    leads_to_export_ids.append(lead["id"])
                elif isinstance(lead, str):
                    leads_to_export_ids.append(lead)
        except Exception as e:
            print(f"[{self.name}] ⚠️ Erreur lors de l'extraction des IDs: {str(e)}")
            print(f"[{self.name}] Format reçu: {export_decision.get('export_decision', {})}")
            self.enhanced_logger.log_error(e, {"step": "extract_lead_ids"})
        
        # Récupérer les leads complets correspondant aux IDs
        leads_to_export = []
        for lead in classified_leads:
            if lead.get("id") in leads_to_export_ids:
                leads_to_export.append(lead)
        
        # Si aucun lead n'est trouvé par ID, sélectionner automatiquement les leads chauds/tièdes
        if not leads_to_export:
            print(f"[{self.name}] ⚠️ Aucun lead correspondant aux IDs trouvé, sélection automatique des leads chauds")
            self.enhanced_logger.log_processing("⚠️ Aucun lead correspondant aux IDs trouvé, sélection automatique des leads chauds")
            
            # Sélectionner tous les leads chauds et tièdes
            for lead in classified_leads:
                # Vérifier la classification via le dictionnaire
                if (isinstance(lead.get("classification"), dict) and 
                    lead.get("classification", {}).get("qualite_lead") in ["WARM", "HOT"]):
                    leads_to_export.append(lead)
                # Vérifier la température via le champ direct
                elif lead.get("gpt_temperature") in ["warm", "hot"]:
                    leads_to_export.append(lead)
                # Vérifier le score (si > 0.7, considéré comme chaud)
                elif lead.get("global_score", 0) > 0.7:
                    leads_to_export.append(lead)
            
            if not leads_to_export:
                # Si toujours aucun lead, prendre les 5 premiers leads
                leads_to_export = classified_leads[:min(5, len(classified_leads))]
                print(f"[{self.name}] ⚠️ Aucun lead chaud trouvé, sélection des {len(leads_to_export)} premiers leads")
                self.enhanced_logger.log_processing(f"⚠️ Aucun lead chaud trouvé, sélection des {len(leads_to_export)} premiers leads")
                
            if not leads_to_export:
                print(f"[{self.name}] ❌ Aucun lead à exporter après la sélection automatique")
                self.enhanced_logger.log_processing("❌ Aucun lead à exporter après la sélection automatique")
                return {"export_status": "failure", "message": "Aucun lead à exporter", "leads_count": 0}
        
        print(f"[{self.name}] Exportation de {len(leads_to_export)} leads vers la base de données Berinia...")
        self.enhanced_logger.log_processing(f"Exportation de {len(leads_to_export)} leads vers la base de données Berinia...")
        
        # Vérifier si l'intégration Berinia est disponible
        if not BERINIA_AVAILABLE:
            error_msg = "Module d'intégration Berinia non disponible. L'exportation est impossible."
            print(f"[{self.name}] ❌ {error_msg}")
            self.enhanced_logger.log_error(error_msg, {"step": "check_integration"})
            return {
                "export_status": "error", 
                "leads_count": 0, 
                "message": error_msg,
                "error": "L'intégration Berinia est nécessaire pour l'exportation des leads"
            }
        
        # Récupérer ou créer un ID de campagne
        campaign_id = None
        
        # 1. Vérifier si un ID de campagne est présent dans les leads
        if len(leads_to_export) > 0 and "campaign_id" in leads_to_export[0]:
            campaign_id_str = leads_to_export[0]["campaign_id"]
            if isinstance(campaign_id_str, str) and campaign_id_str.isdigit():
                campaign_id = int(campaign_id_str)
            elif isinstance(campaign_id_str, int):
                campaign_id = campaign_id_str
                
            print(f"[{self.name}] 📋 ID de campagne trouvé dans les leads: {campaign_id}")
            self.enhanced_logger.log_processing(f"ID de campagne trouvé dans les leads: {campaign_id}")
        
        # 2. Si aucun ID de campagne n'est trouvé, tenter d'obtenir une campagne existante
        if campaign_id is None:
            print(f"[{self.name}] 🔍 Recherche d'une campagne existante...")
            self.enhanced_logger.log_processing("Recherche d'une campagne existante...")
            
            # Récupérer les campagnes existantes
            existing_campaigns = get_all_campaigns()
            if existing_campaigns:
                # Utiliser la campagne la plus récente
                campaign_id = existing_campaigns[0]["id"]
                print(f"[{self.name}] 🔄 Utilisation de la campagne existante: {existing_campaigns[0]['nom']} (ID: {campaign_id})")
                self.enhanced_logger.log_processing(f"Utilisation de la campagne existante: {existing_campaigns[0]['nom']} (ID: {campaign_id})")
        
        # 3. Si aucune campagne existante n'est trouvée, créer une nouvelle campagne
        if campaign_id is None:
            # Créer une campagne avec un nom dynamique basé sur la date
            campaign_name = f"Campagne Auto - {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}"
            campaign_desc = "Campagne créée automatiquement par le CRMExporterAgent"
            
            print(f"[{self.name}] 🔄 Création d'une nouvelle campagne: {campaign_name}")
            self.enhanced_logger.log_processing(f"Création d'une nouvelle campagne: {campaign_name}")
            
            campaign_id = create_campaign_in_berinia(campaign_name, campaign_desc)
            
            if campaign_id is None:
                error_msg = "Impossible de créer une campagne. L'exportation nécessite une campagne valide."
                print(f"[{self.name}] ❌ {error_msg}")
                self.enhanced_logger.log_error(error_msg, {"step": "campaign_creation"})
                return {
                    "export_status": "error",
                    "error": error_msg,
                    "leads_count": 0
                }
            else:
                print(f"[{self.name}] ✅ Nouvelle campagne créée avec succès (ID: {campaign_id})")
                self.enhanced_logger.log_processing(f"Nouvelle campagne créée avec succès (ID: {campaign_id})")
        
        self.enhanced_logger.log_processing(f"ID de campagne final pour l'export: {campaign_id}")
                
        # Exporter les leads vers Berinia
        try:
            export_result = export_leads_to_berinia(leads_to_export, campaign_id)
            
            if export_result.get("success", False):
                print(f"[{self.name}] ✅ Exportation réussie: {export_result.get('leads_count', 0)} leads exportés")
                self.enhanced_logger.log_processing(f"✅ Exportation réussie: {export_result.get('leads_count', 0)} leads exportés")
                return {
                    "export_status": "success",
                    "leads_count": export_result.get("leads_count", 0),
                    "message": f"Export réussi de {export_result.get('leads_count', 0)} leads",
                    "leads_exported": [lead.get("id") for lead in leads_to_export]
                }
            else:
                error_msg = export_result.get("error", "Erreur inconnue")
                print(f"[{self.name}] ❌ Échec de l'exportation: {error_msg}")
                self.enhanced_logger.log_error(f"Échec de l'exportation: {error_msg}", {"result": export_result})
                return {
                    "export_status": "failure",
                    "error": error_msg,
                    "leads_count": 0
                }
            
        except Exception as e:
            error_msg = f"Erreur lors de l'exportation des leads: {str(e)}"
            print(f"[{self.name}] ❌ {error_msg}")
            self.enhanced_logger.log_error(e, {"step": "berinia_export"})
            return {
                "export_status": "error",
                "error": error_msg,
                "leads_count": 0
            }
