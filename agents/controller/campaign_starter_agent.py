from agents.base.base import AgentBase
from utils.llm import ask_gpt_4_1
from logs.agent_logger import log_agent
import datetime
import json
import time

# Import the agents that will be orchestrated
from agents.scraper.apify_scraper import ApifyScraper
from agents.scraper.apollo_scraper import ApolloScraper
from agents.cleaner.lead_cleaner import CleanerAgent
from agents.classifier.lead_classifier_agent import LeadClassifierAgent
from agents.exporter.crm_exporter_agent import CRMExporterAgent
from agents.messenger.messenger_agent import MessengerAgent

class CampaignStarterAgent(AgentBase):
    def __init__(self):
        super().__init__("CampaignStarterAgent")
        self.prompt_path = "prompts/campaign_starter_agent_prompt.txt"
        # Initialize the agents that will be orchestrated
        self.apify_scraper = ApifyScraper()
        self.apollo_scraper = ApolloScraper()
        self.cleaner = CleanerAgent()
        self.classifier = LeadClassifierAgent()
        self.exporter = CRMExporterAgent()
        self.messenger = MessengerAgent()

    def run(self, input_data: dict) -> dict:
        print(f"[{self.name}] 🚀 Démarrage de la campagne...")

        # Extract the validated niche and other information
        validated_niche = input_data.get("validated_niche", {})
        campaign_params = input_data.get("campaign_params", {})
        system_status = input_data.get("system_status", {"status": "READY"})
        campaign_id = input_data.get("campaign_id", f"CAM-{int(time.time())}")

        if not validated_niche:
            result = {"error": "Aucune niche validée fournie", "status": "FAILED"}
            log_agent(self.name, input_data, result)
            return result

        # Prepare the campaign execution plan using GPT-4.1
        try:
            with open(self.prompt_path, "r") as file:
                prompt_template = file.read()
        except Exception as e:
            result = {"error": f"Erreur lors du chargement du prompt: {str(e)}", "status": "FAILED"}
            log_agent(self.name, input_data, result)
            return result

        # Fill in the prompt template
        prompt = prompt_template
        prompt = prompt.replace("{{validated_niche}}", json.dumps(validated_niche))
        prompt = prompt.replace("{{campaign_params}}", json.dumps(campaign_params))
        prompt = prompt.replace("{{system_status}}", json.dumps(system_status))
        prompt = prompt.replace("{{campaign_id}}", campaign_id)

        # Get the execution plan from GPT-4.1
        planning_response_text = ask_gpt_4_1(prompt)
        
        # Parse the JSON response properly
        try:
            # Si la réponse est une chaîne, tenter de la convertir en objet JSON
            if isinstance(planning_response_text, str):
                if "```json" in planning_response_text:
                    json_start = planning_response_text.find("```json") + 7
                    json_end = planning_response_text.find("```", json_start)
                    if json_end > json_start:
                        planning_response_text = planning_response_text[json_start:json_end].strip()
                elif "```" in planning_response_text:
                    json_start = planning_response_text.find("```") + 3
                    json_end = planning_response_text.find("```", json_start)
                    if json_end > json_start:
                        planning_response_text = planning_response_text[json_start:json_end].strip()
                
                # Parser le JSON
                campaign_plan = json.loads(planning_response_text)
            else:
                # Si c'est déjà un dictionnaire, l'utiliser directement
                campaign_plan = planning_response_text
                
        except json.JSONDecodeError as e:
            print(f"[{self.name}] ⚠️ Erreur lors du parsing de la réponse JSON: {str(e)}")
            print(f"[{self.name}] Réponse brute: {planning_response_text[:200]}...")
            
            # Créer un plan par défaut en cas d'erreur
            campaign_plan = {
                "campaign_initialization": {
                    "campaign_id": campaign_id,
                    "niche": validated_niche.get("niche", "Non spécifiée"),
                    "parameters": campaign_params
                },
                "execution_plan": {
                    "phases": [
                        {"name": "scraping", "agents": ["ApifyScraper"], "priority": "high"},
                        {"name": "cleaning", "agents": ["CleanerAgent"], "priority": "high"},
                        {"name": "classification", "agents": ["LeadClassifierAgent"], "priority": "high"},
                        {"name": "export", "agents": ["CRMExporterAgent"], "priority": "medium"}
                    ]
                },
                "error": f"Plan par défaut suite à une erreur de parsing JSON: {str(e)}"
            }
        except Exception as e:
            print(f"[{self.name}] ⚠️ Erreur inattendue lors du traitement du plan: {str(e)}")
            
            # Créer un plan par défaut simplifié
            campaign_plan = {
                "campaign_initialization": {
                    "campaign_id": campaign_id,
                    "niche": validated_niche.get("niche", "Non spécifiée")
                },
                "error": f"Erreur inattendue: {str(e)}"
            }

        # Record the initial plan
        log_agent(self.name, input_data, campaign_plan)

        # Execute the campaign according to the plan
        campaign_result = self._execute_campaign(campaign_plan, validated_niche, campaign_params)

        # Log and return the final results
        log_agent(self.name, campaign_plan, campaign_result)
        return campaign_result

    def _execute_campaign(self, campaign_plan, niche, params):
        """
        Execute the campaign by calling each agent in sequence according to the plan.
        """
        campaign_id = campaign_plan.get("campaign_initialization", {}).get("campaign_id")
        results = {
            "campaign_id": campaign_id,
            "niche": niche.get("niche"),
            "start_time": datetime.datetime.now().isoformat(),
            "phases": {},
            "status": "IN_PROGRESS"
        }

        try:
            # Phase 1: Scraping - Now with multiple scraper options
            print(f"[{self.name}] Phase 1: Scraping des leads pour la niche '{niche.get('niche')}'")
            
            # Determine which scrapers to use based on params
            scraping_params = params.get("scraping", {})
            use_apify = scraping_params.get("use_apify", True)
            use_apollo = scraping_params.get("use_apollo", True)
            
            # If not specified, default to using both
            if not use_apify and not use_apollo:
                use_apify = True
                use_apollo = True
                
            combined_leads = []
            
            # Track scraping metrics
            scraping_metrics = {
                "leads_scraped": 0,
                "time_taken": 0,
                "sources": {}
            }
            
            # Use Apify if requested
            if use_apify:
                apify_input = {
                    "niche": niche.get("niche"),
                    "params": scraping_params.get("apify_params", {}),
                    "campaign_id": campaign_id
                }
                apify_result = self.apify_scraper.run(apify_input)
                
                apify_leads = apify_result.get("leads", [])
                combined_leads.extend(apify_leads)
                
                # Add source tag to each lead
                for lead in apify_leads:
                    lead["source"] = "apify"
                
                # Track Apify metrics
                scraping_metrics["sources"]["apify"] = {
                    "leads_scraped": len(apify_leads),
                    "time_taken": apify_result.get("time_taken", 0)
                }
                scraping_metrics["time_taken"] += apify_result.get("time_taken", 0)
            
            # Use Apollo if requested
            if use_apollo:
                apollo_input = {
                    "niche": niche.get("niche"),
                    "filters": scraping_params.get("apollo_filters", {}),
                    "campaign_id": campaign_id
                }
                apollo_result = self.apollo_scraper.run(apollo_input)
                
                apollo_leads = apollo_result.get("leads", [])
                combined_leads.extend(apollo_leads)
                
                # Add source tag to each lead
                for lead in apollo_leads:
                    if "lead_source" not in lead:  # Avoid overwriting if already set
                        lead["lead_source"] = "apollo"
                
                # Track Apollo metrics
                scraping_metrics["sources"]["apollo"] = {
                    "leads_scraped": len(apollo_leads),
                    "time_taken": apollo_result.get("time_taken", 0)
                }
                scraping_metrics["time_taken"] += apollo_result.get("time_taken", 0)
            
            # Update total lead count
            scraping_metrics["leads_scraped"] = len(combined_leads)
            
            # Store scraping results
            results["phases"]["scraping"] = {
                "status": "COMPLETED" if combined_leads else "FAILED",
                "metrics": scraping_metrics
            }

            # Check if scraping was successful
            if not combined_leads:
                results["status"] = "FAILED"
                results["error"] = "Échec du scraping: aucun lead récupéré"
                return results

            # Phase 2: Cleaning
            print(f"[{self.name}] Phase 2: Nettoyage des {len(combined_leads)} leads")
            cleaning_input = {
                "data": combined_leads,
                "campaign_id": campaign_id
            }
            cleaning_result = self.cleaner.run(cleaning_input)
            results["phases"]["cleaning"] = {
                "status": "COMPLETED" if cleaning_result.get("clean_data", []) else "FAILED",
                "metrics": {
                    "leads_cleaned": len(cleaning_result.get("clean_data", [])),
                    "leads_rejected": len(cleaning_result.get("rejected_leads", []))
                }
            }

            # Check if cleaning was successful
            if not cleaning_result.get("clean_data", []):
                results["status"] = "FAILED"
                results["error"] = "Échec du nettoyage: aucun lead propre"
                return results

            # Phase 3: Classification
            print(f"[{self.name}] Phase 3: Classification des {len(cleaning_result.get('clean_data', []))} leads nettoyés")
            classification_input = {
                "clean_leads": cleaning_result.get("clean_data", []),
                "campaign_id": campaign_id
            }
            classification_result = self.classifier.run(classification_input)

            # Extract classification metrics
            classified_leads = classification_result.get("classified_leads", [])
            hot_leads = [l for l in classified_leads if l.get("classification", {}).get("qualite_lead") == "CHAUD"]
            warm_leads = [l for l in classified_leads if l.get("classification", {}).get("qualite_lead") == "TIÈDE"]
            cold_leads = [l for l in classified_leads if l.get("classification", {}).get("qualite_lead") == "FROID"]

            results["phases"]["classification"] = {
                "status": "COMPLETED" if classified_leads else "FAILED",
                "metrics": {
                    "leads_classified": len(classified_leads),
                    "hot_leads": len(hot_leads),
                    "warm_leads": len(warm_leads),
                    "cold_leads": len(cold_leads)
                }
            }

            # Check if classification was successful
            if not classified_leads:
                results["status"] = "FAILED"
                results["error"] = "Échec de la classification: aucun lead classifié"
                return results

            # Phase 4: CRM Export
            print(f"[{self.name}] Phase 4: Décision d'export CRM pour {len(classified_leads)} leads classifiés")
            export_input = {
                "classified_leads": classified_leads,
                "campaign_id": campaign_id,
                # Additional export parameters could be added here
                "daily_limit": params.get("crm", {}).get("daily_limit", 50),
                "exported_today": params.get("crm", {}).get("exported_today", 0)
            }
            export_result = self.exporter.run(export_input)

            leads_to_export = export_result.get("export_decision", {}).get("leads_to_export_now", [])
            leads_delayed = export_result.get("export_decision", {}).get("leads_to_delay", [])

            results["phases"]["export"] = {
                "status": "COMPLETED",
                "metrics": {
                    "leads_exported": len(leads_to_export),
                    "leads_delayed": len(leads_delayed),
                    "export_strategy": export_result.get("export_decision", {}).get("batching_strategy", {}).get("methode", "N/A")
                }
            }

            # Phase 5: Messenger - Contact strategy
            if leads_to_export:
                print(f"[{self.name}] Phase 5: Stratégie de contact pour {len(leads_to_export)} leads exportés")
                contact_input = {
                    "leads_to_contact": leads_to_export,
                    "campaign_id": campaign_id,
                    # Add contact parameters
                    "timezone": params.get("contact", {}).get("timezone", "Europe/Paris")
                }
                contact_result = self.messenger.run(contact_input)

                contact_strategies = contact_result.get("contact_strategy", [])

                results["phases"]["contact"] = {
                    "status": "COMPLETED" if contact_strategies else "FAILED",
                    "metrics": {
                        "leads_contacted": len(contact_strategies),
                        "by_channel": contact_result.get("summary", {}).get("contacts_par_canal", {})
                    }
                }
            else:
                results["phases"]["contact"] = {
                    "status": "SKIPPED",
                    "reason": "Aucun lead à contacter immédiatement"
                }

            # Final campaign status
            results["status"] = "COMPLETED"
            results["end_time"] = datetime.datetime.now().isoformat()
            results["summary"] = {
                "leads_scraped": results["phases"]["scraping"]["metrics"]["leads_scraped"],
                "leads_cleaned": results["phases"]["cleaning"]["metrics"]["leads_cleaned"],
                "leads_classified": results["phases"]["classification"]["metrics"]["leads_classified"],
                "leads_exported": results["phases"]["export"]["metrics"]["leads_exported"],
                "leads_contacted": results["phases"]["contact"]["metrics"].get("leads_contacted", 0) if results["phases"].get("contact", {}).get("status") == "COMPLETED" else 0
            }
            
            # Sauvegarder la campagne dans le stockage
            try:
                from db.campaign_storage import save_campaign
                save_success = save_campaign(results)
                if save_success:
                    print(f"[{self.name}] ✅ Campagne {campaign_id} sauvegardée avec succès")
                else:
                    print(f"[{self.name}] ⚠️ Erreur lors de la sauvegarde de la campagne {campaign_id}")
            except Exception as e:
                print(f"[{self.name}] ⚠️ Exception lors de la sauvegarde de la campagne: {str(e)}")

            return results

        except Exception as e:
            results["status"] = "ERROR"
            results["error"] = f"Erreur pendant l'exécution de la campagne: {str(e)}"
            return results
