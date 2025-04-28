from agents.base.base import AgentBase
from utils.llm import ask_gpt_4_1
from logs.agent_logger import log_agent
from agents.messenger.email_sender import EmailSender
from agents.messenger.sms_sender import SMSSender
import json
import datetime
import os
import re

class MessengerAgent(AgentBase):
    def __init__(self):
        super().__init__("MessengerAgent")
        self.prompt_path = "prompts/messenger_agent_prompt.txt"
        self.templates_dir = "templates/messages"
        self.email_sender = EmailSender()
        self.sms_sender = SMSSender()
        self.message_history_path = "logs/message_history.json"
        self.response_stats_path = "logs/response_stats.json"
        self.followup_schedule_path = "config/followup_schedule.json"
        self.channel_stats_path = "logs/channel_stats.json"
        self._ensure_files_exist()
    
    def _ensure_files_exist(self):
        """Ensures that necessary directories and files for messaging exist"""
        # Ensure templates directory
        if not os.path.exists(self.templates_dir):
            os.makedirs(self.templates_dir, exist_ok=True)
            
            # Create default templates directory for different niches
            niches = ["general", "coiffeur", "plombier", "avocat", "consultant", "restaurant"]
            for niche in niches:
                niche_dir = f"{self.templates_dir}/{niche}"
                if not os.path.exists(niche_dir):
                    os.makedirs(niche_dir, exist_ok=True)
                    
                    # Create default email template for the niche
                    with open(f"{niche_dir}/email_template.txt", "w") as f:
                        f.write("Sujet: {{subject}}\n\nBonjour {{name}},\n\n{{message_body}}\n\nCordialement,\nL'équipe {{company}}")
                    
                    # Create default SMS template for the niche
                    with open(f"{niche_dir}/sms_template.txt", "w") as f:
                        f.write("{{company}}: {{message_body}} Répondez STOP pour vous désinscrire.")
        
        # Ensure message history file
        if not os.path.exists(self.message_history_path):
            message_history = {
                "messages": [],
                "last_updated": datetime.datetime.now().isoformat()
            }
            
            os.makedirs(os.path.dirname(self.message_history_path), exist_ok=True)
            with open(self.message_history_path, "w") as f:
                json.dump(message_history, f, indent=2)
        
        # Ensure response stats file
        if not os.path.exists(self.response_stats_path):
            response_stats = {
                "global": {
                    "sent": 0,
                    "delivered": 0,
                    "opened": 0,
                    "clicked": 0,
                    "replied": 0,
                    "response_rate": 0.0,
                    "last_updated": datetime.datetime.now().isoformat()
                },
                "by_niche": {},
                "by_template": {},
                "by_channel": {
                    "email": {
                        "sent": 0,
                        "delivered": 0,
                        "opened": 0,
                        "clicked": 0,
                        "replied": 0,
                        "response_rate": 0.0
                    },
                    "sms": {
                        "sent": 0,
                        "delivered": 0,
                        "replied": 0,
                        "response_rate": 0.0
                    }
                }
            }
            
            os.makedirs(os.path.dirname(self.response_stats_path), exist_ok=True)
            with open(self.response_stats_path, "w") as f:
                json.dump(response_stats, f, indent=2)
        
        # Ensure followup schedule
        if not os.path.exists(self.followup_schedule_path):
            followup_schedule = {
                "default": {
                    "intervals": [1, 3, 7, 14, 30],  # Days after initial message
                    "max_followups": 3,
                    "hours": {
                        "start": 9,  # 9 AM
                        "end": 17    # 5 PM
                    },
                    "weekend_allowed": False
                },
                "by_niche": {
                    "urgent": {
                        "intervals": [1, 2, 5],
                        "max_followups": 2,
                        "hours": {
                            "start": 8,
                            "end": 19
                        },
                        "weekend_allowed": True
                    }
                },
                "by_temperature": {
                    "hot": {
                        "intervals": [1, 2, 5, 10],
                        "max_followups": 4
                    },
                    "warm": {
                        "intervals": [2, 5, 10, 20],
                        "max_followups": 3
                    },
                    "cold": {
                        "intervals": [3, 10, 20],
                        "max_followups": 2
                    }
                },
                "last_updated": datetime.datetime.now().isoformat()
            }
            
            os.makedirs(os.path.dirname(self.followup_schedule_path), exist_ok=True)
            with open(self.followup_schedule_path, "w") as f:
                json.dump(followup_schedule, f, indent=2)
        
        # Ensure channel stats file
        if not os.path.exists(self.channel_stats_path):
            channel_stats = {
                "by_niche": {},
                "by_temperature": {
                    "hot": {
                        "email": 0.6,
                        "sms": 0.4
                    },
                    "warm": {
                        "email": 0.7,
                        "sms": 0.3
                    },
                    "cold": {
                        "email": 0.8,
                        "sms": 0.2
                    }
                },
                "global_preference": {
                    "email": 0.7,
                    "sms": 0.3
                },
                "last_updated": datetime.datetime.now().isoformat()
            }
            
            os.makedirs(os.path.dirname(self.channel_stats_path), exist_ok=True)
            with open(self.channel_stats_path, "w") as f:
                json.dump(channel_stats, f, indent=2)
    
    def run(self, input_data: dict) -> dict:
        print(f"[{self.name}] 💬 Envoi de messages...")
        
        # Extraire les paramètres d'entrée
        operation = input_data.get("operation", "send")
        leads = input_data.get("leads", [])
        channel = input_data.get("channel", "auto")  # "email", "sms", ou "auto"
        template_key = input_data.get("template", "general")
        niche = input_data.get("niche", "general")
        campaign_id = input_data.get("campaign_id", None)
        custom_message = input_data.get("custom_message", None)
        is_followup = input_data.get("is_followup", False)
        
        # Préparer le résultat
        result = {
            "operation": operation,
            "campaign_id": campaign_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "status": "PROCESSING"
        }
        
        try:
            # Charger les données nécessaires
            message_history = self._load_message_history()
            response_stats = self._load_response_stats()
            followup_schedule = self._load_followup_schedule()
            channel_stats = self._load_channel_stats()
            
            # Exécuter l'opération demandée
            if operation == "send":
                # Envoyer des messages aux leads
                if not leads:
                    result["error"] = "Aucun lead fourni pour l'envoi de messages"
                    result["status"] = "FAILED"
                    log_agent(self.name, input_data, result)
                    return result
                
                # Charger le prompt pour la personnalisation des messages
                try:
                    with open(self.prompt_path, "r") as file:
                        prompt_template = file.read()
                except Exception as e:
                    result["error"] = f"Erreur lors du chargement du prompt: {str(e)}"
                    result["status"] = "FAILED"
                    log_agent(self.name, input_data, result)
                    return result
                
                # Préparer et envoyer les messages pour chaque lead
                sent_messages = []
                for lead in leads:
                    # Déterminer le canal à utiliser (email, SMS ou les deux)
                    lead_channel = self._select_optimal_channel(lead, channel, niche, channel_stats)
                    
                    # Construire le message pour chaque canal
                    message_result = {}
                    
                    if lead_channel in ["email", "both"]:
                        # Préparer et envoyer un email
                        email_result = self._prepare_and_send_email(
                            lead, 
                            niche, 
                            template_key, 
                            prompt_template, 
                            custom_message,
                            is_followup
                        )
                        message_result["email"] = email_result
                    
                    if lead_channel in ["sms", "both"]:
                        # Préparer et envoyer un SMS
                        sms_result = self._prepare_and_send_sms(
                            lead, 
                            niche, 
                            template_key, 
                            prompt_template, 
                            custom_message,
                            is_followup
                        )
                        message_result["sms"] = sms_result
                    
                    # Programmer les éventuels messages de suivi
                    if not is_followup:  # Ne pas programmer de suivi pour les suivis
                        followup = self._schedule_followup(lead, niche, followup_schedule)
                        message_result["followup"] = followup
                    
                    # Enregistrer le message dans l'historique
                    message_entry = {
                        "lead_id": lead.get("id"),
                        "lead_name": lead.get("name"),
                        "lead_email": lead.get("email"),
                        "lead_phone": lead.get("phone"),
                        "niche": niche,
                        "channel": lead_channel,
                        "template_key": template_key,
                        "is_followup": is_followup,
                        "timestamp": datetime.datetime.now().isoformat(),
                        "status": "sent",
                        "campaign_id": campaign_id
                    }
                    
                    message_history["messages"].append(message_entry)
                    sent_messages.append({
                        "lead_id": lead.get("id"),
                        "channels": lead_channel,
                        "result": message_result
                    })
                
                # Mettre à jour les statistiques
                response_stats = self._update_stats_after_sending(sent_messages, niche, template_key, response_stats)
                
                # Enregistrer les mises à jour
                self._save_message_history(message_history)
                self._save_response_stats(response_stats)
                
                # Préparer le résultat
                result["sent_messages"] = sent_messages
                result["stats"] = {
                    "total_sent": len(sent_messages),
                    "by_channel": {
                        "email": len([m for m in sent_messages if m["channels"] in ["email", "both"]]),
                        "sms": len([m for m in sent_messages if m["channels"] in ["sms", "both"]]),
                        "both": len([m for m in sent_messages if m["channels"] == "both"])
                    }
                }
                result["status"] = "COMPLETED"
            
            elif operation == "process_responses":
                # Traiter les réponses reçues
                responses = input_data.get("responses", [])
                
                if not responses:
                    result["error"] = "Aucune réponse à traiter"
                    result["status"] = "FAILED"
                    log_agent(self.name, input_data, result)
                    return result
                
                # Traiter chaque réponse
                processed_responses = []
                for response in responses:
                    processed = self._process_response(response, message_history, response_stats)
                    processed_responses.append(processed)
                
                # Enregistrer les mises à jour
                self._save_message_history(message_history)
                self._save_response_stats(response_stats)
                
                # Mettre à jour les statistiques de canal
                channel_stats = self._update_channel_stats(responses, channel_stats)
                self._save_channel_stats(channel_stats)
                
                # Préparer le résultat
                result["processed_responses"] = processed_responses
                result["stats"] = {
                    "total_processed": len(processed_responses),
                    "positive_responses": len([r for r in processed_responses if r["sentiment"] == "positive"]),
                    "negative_responses": len([r for r in processed_responses if r["sentiment"] == "negative"]),
                    "neutral_responses": len([r for r in processed_responses if r["sentiment"] == "neutral"])
                }
                result["status"] = "COMPLETED"
            
            elif operation == "update_template":
                # Mettre à jour un modèle de message
                template_content = input_data.get("template_content")
                template_type = input_data.get("template_type", "email")  # "email" ou "sms"
                
                if not template_content:
                    result["error"] = "Aucun contenu de modèle fourni"
                    result["status"] = "FAILED"
                    log_agent(self.name, input_data, result)
                    return result
                
                # Enregistrer le nouveau modèle
                template_path = f"{self.templates_dir}/{niche}/{template_type}_template.txt"
                
                # S'assurer que le répertoire existe
                os.makedirs(os.path.dirname(template_path), exist_ok=True)
                
                with open(template_path, "w") as f:
                    f.write(template_content)
                
                # Préparer le résultat
                result["template_updated"] = {
                    "niche": niche,
                    "type": template_type,
                    "path": template_path
                }
                result["status"] = "COMPLETED"
            
            elif operation == "analyze_performance":
                # Analyser les performances des messages
                analysis_period = input_data.get("period", "all")
                analysis_niche = input_data.get("analysis_niche", "all")
                
                # Effectuer l'analyse
                performance_analysis = self._analyze_message_performance(
                    message_history, 
                    response_stats, 
                    analysis_period, 
                    analysis_niche
                )
                
                # Préparer le résultat
                result["performance"] = performance_analysis
                result["status"] = "COMPLETED"
            
            elif operation == "manage_followups":
                # Gérer les suivis programmés
                followups_due = self._get_pending_followups(message_history, followup_schedule)
                
                if not followups_due:
                    result["message"] = "Aucun suivi à envoyer pour le moment"
                    result["status"] = "COMPLETED"
                    log_agent(self.name, input_data, result)
                    return result
                
                # Préparer les données pour envoi des suivis
                followup_data = {
                    "operation": "send",
                    "leads": followups_due["leads"],
                    "channel": "auto",  # Utiliser le canal optimal pour chaque suivi
                    "niche": followups_due.get("niche", "general"),
                    "campaign_id": campaign_id,
                    "is_followup": True
                }
                
                # Appeler l'opération d'envoi avec les données de suivi
                followup_result = self.run(followup_data)
                
                # Préparer le résultat
                result["followups_sent"] = followup_result.get("sent_messages", [])
                result["stats"] = followup_result.get("stats", {})
                result["status"] = "COMPLETED"
            
            elif operation == "update_followup_schedule":
                # Mettre à jour le planning de suivi
                new_schedule = input_data.get("new_schedule")
                
                if not new_schedule:
                    result["error"] = "Aucun planning de suivi fourni"
                    result["status"] = "FAILED"
                    log_agent(self.name, input_data, result)
                    return result
                
                # Mettre à jour le planning
                updated_schedule = self._update_followup_schedule(new_schedule, followup_schedule)
                
                # Enregistrer le planning mis à jour
                self._save_followup_schedule(updated_schedule)
                
                # Préparer le résultat
                result["updated_schedule"] = updated_schedule
                result["status"] = "COMPLETED"
            
            else:
                result["error"] = f"Opération non reconnue: {operation}"
                result["status"] = "FAILED"
        
        except Exception as e:
            result["error"] = f"Erreur lors de l'exécution de l'opération: {str(e)}"
            result["status"] = "FAILED"
        
        # Enregistrer les logs
        log_agent(self.name, input_data, result)
        
        return result
    
    def _load_message_history(self):
        """
        Charge l'historique des messages envoyés
        """
        try:
            with open(self.message_history_path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"[{self.name}] ⚠️ Erreur lors du chargement de l'historique des messages: {str(e)}")
            return {"messages": [], "last_updated": datetime.datetime.now().isoformat()}
    
    def _load_response_stats(self):
        """
        Charge les statistiques de réponse aux messages
        """
        try:
            with open(self.response_stats_path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"[{self.name}] ⚠️ Erreur lors du chargement des statistiques de réponse: {str(e)}")
            return {"global": {}, "by_niche": {}, "by_template": {}, "by_channel": {}}
    
    def _load_followup_schedule(self):
        """
        Charge le planning des suivis
        """
        try:
            with open(self.followup_schedule_path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"[{self.name}] ⚠️ Erreur lors du chargement du planning des suivis: {str(e)}")
            return {"default": {}}
    
    def _load_channel_stats(self):
        """
        Charge les statistiques par canal
        """
        try:
            with open(self.channel_stats_path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"[{self.name}] ⚠️ Erreur lors du chargement des statistiques par canal: {str(e)}")
            return {"by_niche": {}, "by_temperature": {}, "global_preference": {}}
    
    def _save_message_history(self, message_history):
        """
        Sauvegarde l'historique des messages
        """
        try:
            message_history["last_updated"] = datetime.datetime.now().isoformat()
            with open(self.message_history_path, "w") as f:
                json.dump(message_history, f, indent=2)
            return True
        except Exception as e:
            print(f"[{self.name}] ⚠️ Erreur lors de la sauvegarde de l'historique des messages: {str(e)}")
            return False
    
    def _save_response_stats(self, response_stats):
        """
        Sauvegarde les statistiques de réponse
        """
        try:
            response_stats["global"]["last_updated"] = datetime.datetime.now().isoformat()
            with open(self.response_stats_path, "w") as f:
                json.dump(response_stats, f, indent=2)
            return True
        except Exception as e:
            print(f"[{self.name}] ⚠️ Erreur lors de la sauvegarde des statistiques de réponse: {str(e)}")
            return False
    
    def _save_followup_schedule(self, followup_schedule):
        """
        Sauvegarde le planning des suivis
        """
        try:
            followup_schedule["last_updated"] = datetime.datetime.now().isoformat()
            with open(self.followup_schedule_path, "w") as f:
                json.dump(followup_schedule, f, indent=2)
            return True
        except Exception as e:
            print(f"[{self.name}] ⚠️ Erreur lors de la sauvegarde du planning des suivis: {str(e)}")
            return False
    
    def _save_channel_stats(self, channel_stats):
        """
        Sauvegarde les statistiques par canal
        """
        try:
            channel_stats["last_updated"] = datetime.datetime.now().isoformat()
            with open(self.channel_stats_path, "w") as f:
                json.dump(channel_stats, f, indent=2)
            return True
        except Exception as e:
            print(f"[{self.name}] ⚠️ Erreur lors de la sauvegarde des statistiques par canal: {str(e)}")
            return False
    
    def _select_optimal_channel(self, lead, channel_preference, niche, channel_stats):
        """
        Sélectionne le canal optimal pour l'envoi du message
        """
        # Si un canal spécifique est demandé et disponible, l'utiliser
        if channel_preference == "email" and lead.get("email"):
            return "email"
        elif channel_preference == "sms" and lead.get("phone"):
            return "sms"
        elif channel_preference == "both" and lead.get("email") and lead.get("phone"):
            return "both"
        
        # Si le canal est "auto", déterminer le meilleur canal
        if channel_preference == "auto":
            # Vérifier quels canaux sont disponibles
            has_email = bool(lead.get("email"))
            has_phone = bool(lead.get("phone"))
            
            if has_email and has_phone:
                # Les deux canaux sont disponibles, choisir le meilleur selon les stats
                
                # 1. Vérifier les stats spécifiques à la niche
                if niche in channel_stats.get("by_niche", {}):
                    niche_stats = channel_stats["by_niche"][niche]
                    email_rate = niche_stats.get("email", 0.5)
                    sms_rate = niche_stats.get("sms", 0.5)
                    
                    if email_rate >= 0.7 and sms_rate >= 0.7:
                        return "both"  # Les deux canaux sont efficaces
                    elif email_rate > sms_rate:
                        return "email"
                    else:
                        return "sms"
                
                # 2. Vérifier les stats selon la température du lead (si disponible)
                if "temperature" in lead:
                    temp = lead["temperature"]
                    if temp in channel_stats.get("by_temperature", {}):
                        temp_stats = channel_stats["by_temperature"][temp]
                        
                        if temp_stats.get("email", 0.5) > temp_stats.get("sms", 0.5):
                            return "email"
                        else:
                            return "sms"
                
                # 3. Utiliser la préférence globale par défaut
                global_pref = channel_stats.get("global_preference", {})
                if global_pref.get("email", 0.5) > global_pref.get("sms", 0.5):
                    return "email"
                else:
                    return "sms"
            
            # Un seul canal est disponible
            elif has_email:
                return "email"
            elif has_phone:
                return "sms"
            else:
                # Aucun canal disponible
                return None
        
        # Par défaut, essayer email
        if lead.get("email"):
            return "email"
        elif lead.get("phone"):
            return "sms"
        else:
            return None
    
    def _prepare_and_send_email(self, lead, niche, template_key, prompt_template, custom_message, is_followup):
        """
        Prépare et envoie un email au lead
        """
        try:
            # Charger le template d'email pour la niche
            template_path = f"{self.templates_dir}/{niche}/email_template.txt"
            
            # Si le template n'existe pas pour cette niche, utiliser le template général
            if not os.path.exists(template_path):
                template_path = f"{self.templates_dir}/general/email_template.txt"
            
            # Charger le template
            with open(template_path, "r") as f:
                template = f.read()
            
            # Extraire le sujet du template (première ligne commençant par "Sujet: ")
            subject_line = re.search(r"Sujet: (.*)\n", template)
            if subject_line:
                subject = subject_line.group(1)
                template = template.replace(f"Sujet: {subject}\n", "")
            else:
                subject = f"Information importante pour {lead.get('name', 'vous')}"
            
            # Personnaliser le sujet
            company_name = "Notre entreprise"  # À remplacer par le nom réel de l'entreprise
            personalized_subject = subject.replace("{{subject}}", f"Information pour {lead.get('name', 'vous')}")
            personalized_subject = personalized_subject.replace("{{name}}", lead.get("name", ""))
            personalized_subject = personalized_subject.replace("{{company}}", company_name)
            
            # Préparer le contenu du message
            if custom_message:
                message_body = custom_message
            else:
                # Générer un message personnalisé avec GPT
                prompt = prompt_template.replace("{{operation}}", "generate_message")
                prompt = prompt.replace("{{channel}}", "email")
                prompt = prompt.replace("{{lead_data}}", json.dumps(lead, ensure_ascii=False))
                prompt = prompt.replace("{{niche}}", niche)
                prompt = prompt.replace("{{is_followup}}", str(is_followup).lower())
                
                # Ajouter un contexte spécifique pour les suivis
                if is_followup:
                    prompt = prompt.replace("{{followup_context}}", "C'est un message de suivi après un premier contact.")
                else:
                    prompt = prompt.replace("{{followup_context}}", "C'est un premier contact avec ce lead.")
                
                # Appeler GPT-4.1 pour générer le message
                message_content = ask_gpt_4_1(prompt)
                message_body = message_content.get("message", "")
            
            # Personnaliser le template avec les informations du lead
            personalized_email = template.replace("{{message_body}}", message_body)
            personalized_email = personalized_email.replace("{{name}}", lead.get("name", ""))
            personalized_email = personalized_email.replace("{{company}}", company_name)
            
            # Envoyer l'email
            email_result = self.email_sender.send_email(
                to_email=lead.get("email"),
                subject=personalized_subject,
                body=personalized_email
            )
            
            return {
                "status": email_result.get("status", "failed"),
                "message_id": email_result.get("message_id", None),
                "subject": personalized_subject,
                "content_preview": message_body[:100] + "..." if len(message_body) > 100 else message_body
            }
        
        except Exception as e:
            print(f"[{self.name}] ⚠️ Erreur lors de la préparation et l'envoi de l'email: {str(e)}")
            return {"status": "failed", "error": str(e)}
    
    def _prepare_and_send_sms(self, lead, niche, template_key, prompt_template, custom_message, is_followup):
        """
        Prépare et envoie un SMS au lead
        """
        try:
            # Charger le template SMS pour la niche
            template_path = f"{self.templates_dir}/{niche}/sms_template.txt"
            
            # Si le template n'existe pas pour cette niche, utiliser le template général
            if not os.path.exists(template_path):
                template_path = f"{self.templates_dir}/general/sms_template.txt"
            
            # Charger le template
            with open(template_path, "r") as f:
                template = f.read()
            
            # Préparer le contenu du message
            if custom_message:
                message_body = custom_message
            else:
                # Générer un message personnalisé avec GPT
                prompt = prompt_template.replace("{{operation}}", "generate_message")
                prompt = prompt.replace("{{channel}}", "sms")
                prompt = prompt.replace("{{lead_data}}", json.dumps(lead, ensure_ascii=False))
                prompt = prompt.replace("{{niche}}", niche)
                prompt = prompt.replace("{{is_followup}}", str(is_followup).lower())
                
                # Ajouter un contexte spécifique pour les suivis
                if is_followup:
                    prompt = prompt.replace("{{followup_context}}", "C'est un message de suivi après un premier contact.")
                else:
                    prompt = prompt.replace("{{followup_context}}", "C'est un premier contact avec ce lead.")
                
                # Appeler GPT-4.1 pour générer le message
                message_content = ask_gpt_4_1(prompt)
                message_body = message_content.get("message", "")
            
            # Personnaliser le template avec les informations du lead
            company_name = "Notre entreprise"  # À remplacer par le nom réel de l'entreprise
            personalized_sms = template.replace("{{message_body}}", message_body)
            personalized_sms = personalized_sms.replace("{{name}}", lead.get("name", ""))
            personalized_sms = personalized_sms.replace("{{company}}", company_name)
            
            # S'assurer que le SMS respecte la limite de caractères (160 pour les SMS standards)
            if len(personalized_sms) > 160:
                personalized_sms = personalized_sms[:157] + "..."
            
            # Envoyer le SMS
            sms_result = self.sms_sender.send_sms(
                to_phone=lead.get("phone"),
                message=personalized_sms
            )
            
            return {
                "status": sms_result.get("status", "failed"),
                "message_id": sms_result.get("message_id", None),
                "content_preview": personalized_sms[:50] + "..." if len(personalized_sms) > 50 else personalized_sms
            }
        
        except Exception as e:
            print(f"[{self.name}] ⚠️ Erreur lors de la préparation et l'envoi du SMS: {str(e)}")
            return {"status": "failed", "error": str(e)}
    
    def _schedule_followup(self, lead, niche, followup_schedule):
        """
        Programme des messages de suivi pour un lead
        """
        try:
            lead_temperature = lead.get("temperature", "warm")
            
            # Déterminer le planning à utiliser
            schedule = None
            
            # 1. Vérifier s'il y a un planning spécifique pour la niche
            if niche in followup_schedule.get("by_niche", {}):
                schedule = followup_schedule["by_niche"][niche]
            # 2. Vérifier s'il y a un planning spécifique pour la température
            elif lead_temperature in followup_schedule.get("by_temperature", {}):
                schedule = followup_schedule["by_temperature"][lead_temperature]
            # 3. Utiliser le planning par défaut
            else:
                schedule = followup_schedule.get("default", {})
            
            if not schedule:
                return {"status": "failed", "error": "Aucun planning de suivi trouvé"}
            
            # Récupérer les intervalles et le nombre max de suivis
            intervals = schedule.get("intervals", [1, 3, 7])
            max_followups = schedule.get("max_followups", 2)
            
            # Limiter le nombre d'intervalles au nombre max de suivis
            intervals = intervals[:max_followups]
            
            # Calculer les dates de suivi
            followup_dates = []
            now = datetime.datetime.now()
            
            for days in intervals:
                followup_date = now + datetime.timedelta(days=days)
                
                # Vérifier si la date tombe un week-end et si les week-ends sont autorisés
                is_weekend = followup_date.weekday() >= 5  # 5=samedi, 6=dimanche
                
                if is_weekend and not schedule.get("weekend_allowed", False):
                    # Déplacer au lundi suivant
                    days_to_add = 7 - followup_date.weekday() + 1
                    followup_date = followup_date + datetime.timedelta(days=days_to_add)
                
                # Appliquer les heures de travail
                hours = schedule.get("hours", {"start": 9, "end": 17})
                followup_date = followup_date.replace(
                    hour=hours.get("start", 9),
                    minute=0,
                    second=0,
                    microsecond=0
                )
                
                followup_dates.append(followup_date.isoformat())
            
            return {
                "status": "scheduled",
                "lead_id": lead.get("id"),
                "followup_dates": followup_dates,
                "max_followups": max_followups
            }
        
        except Exception as e:
            print(f"[{self.name}] ⚠️ Erreur lors de la programmation des suivis: {str(e)}")
            return {"status": "failed", "error": str(e)}
    
    def _update_stats_after_sending(self, sent_messages, niche, template_key, response_stats):
        """
        Met à jour les statistiques après l'envoi de messages
        """
        try:
            # Mettre à jour les statistiques globales
            global_stats = response_stats.get("global", {})
            global_stats["sent"] = global_stats.get("sent", 0) + len(sent_messages)
            
            # Mettre à jour les statistiques par niche
            if niche not in response_stats.get("by_niche", {}):
                response_stats["by_niche"][niche] = {
                    "sent": 0,
                    "delivered": 0,
                    "opened": 0,
                    "clicked": 0,
                    "replied": 0,
                    "response_rate": 0.0
                }
            
            niche_stats = response_stats["by_niche"][niche]
            niche_stats["sent"] = niche_stats.get("sent", 0) + len(sent_messages)
            
            # Mettre à jour les statistiques par template
            if template_key not in response_stats.get("by_template", {}):
                response_stats["by_template"][template_key] = {
                    "sent": 0,
                    "delivered": 0,
                    "opened": 0,
                    "clicked": 0,
                    "replied": 0,
                    "response_rate": 0.0
                }
            
            template_stats = response_stats["by_template"][template_key]
            template_stats["sent"] = template_stats.get("sent", 0) + len(sent_messages)
            
            # Mettre à jour les statistiques par canal
            channel_stats = response_stats.get("by_channel", {})
            
            # Compter les messages par canal
            email_count = len([m for m in sent_messages if "email" in m.get("result", {})])
            sms_count = len([m for m in sent_messages if "sms" in m.get("result", {})])
            
            # Email
            if "email" not in channel_stats:
                channel_stats["email"] = {
                    "sent": 0,
                    "delivered": 0,
                    "opened": 0,
                    "clicked": 0,
                    "replied": 0,
                    "response_rate": 0.0
                }
            
            email_stats = channel_stats["email"]
            email_stats["sent"] = email_stats.get("sent", 0) + email_count
            
            # SMS
            if "sms" not in channel_stats:
                channel_stats["sms"] = {
                    "sent": 0,
                    "delivered": 0,
                    "replied": 0,
                    "response_rate": 0.0
                }
            
            sms_stats = channel_stats["sms"]
            sms_stats["sent"] = sms_stats.get("sent", 0) + sms_count
            
            return response_stats
        
        except Exception as e:
            print(f"[{self.name}] ⚠️ Erreur lors de la mise à jour des statistiques: {str(e)}")
            return response_stats
    
    def _process_response(self, response, message_history, response_stats):
        """
        Traite une réponse reçue à un message
        """
        try:
            # Extraire les informations de la réponse
            lead_id = response.get("lead_id")
            channel = response.get("channel")  # "email" ou "sms"
            content = response.get("content", "")
            timestamp = response.get("timestamp", datetime.datetime.now().isoformat())
            
            # Analyser le contenu de la réponse avec GPT
            # Charger le prompt pour l'analyse des réponses
            try:
                with open(self.prompt_path, "r") as file:
                    prompt_template = file.read()
            except Exception as e:
                print(f"[{self.name}] ⚠️ Erreur lors du chargement du prompt: {str(e)}")
                return {"status": "failed", "error": str(e)}
            
            # Construire le prompt pour l'analyse
            prompt = prompt_template.replace("{{operation}}", "analyze_response")
            prompt = prompt.replace("{{channel}}", channel)
            prompt = prompt.replace("{{response_content}}", content)
            
            # Appeler GPT-4.1 pour l'analyse
            analysis = ask_gpt_4_1(prompt)
            
            sentiment = analysis.get("sentiment", "neutral")
            interest_level = analysis.get("interest_level", 0.5)
            needs_further_action = analysis.get("needs_further_action", False)
            suggested_actions = analysis.get("suggested_actions", [])
            
            # Mettre à jour l'historique des messages
            for message in message_history.get("messages", []):
                if message.get("lead_id") == lead_id and message.get("channel") == channel:
                    # Mettre à jour le statut du message
                    message["status"] = "replied"
                    message["response"] = {
                        "content": content,
                        "timestamp": timestamp,
                        "sentiment": sentiment,
                        "interest_level": interest_level
                    }
            
            # Mettre à jour les statistiques de réponse
            global_stats = response_stats.get("global", {})
            global_stats["replied"] = global_stats.get("replied", 0) + 1
            
            if global_stats.get("sent", 0) > 0:
                global_stats["response_rate"] = global_stats.get("replied", 0) / global_stats.get("sent", 1)
            
            # Statistiques par canal
            channel_stats = response_stats.get("by_channel", {}).get(channel, {})
            channel_stats["replied"] = channel_stats.get("replied", 0) + 1
            
            if channel_stats.get("sent", 0) > 0:
                channel_stats["response_rate"] = channel_stats.get("replied", 0) / channel_stats.get("sent", 1)
            
            # Préparer le résultat du traitement
            processed_response = {
                "lead_id": lead_id,
                "channel": channel,
                "timestamp": timestamp,
                "sentiment": sentiment,
                "interest_level": interest_level,
                "needs_further_action": needs_further_action,
                "suggested_actions": suggested_actions
            }
            
            return processed_response
        
        except Exception as e:
            print(f"[{self.name}] ⚠️ Erreur lors du traitement de la réponse: {str(e)}")
            return {"status": "failed", "error": str(e)}
    
    def _update_channel_stats(self, responses, channel_stats):
        """
        Met à jour les statistiques par canal en fonction des réponses reçues
        """
        try:
            # Collecter les données par niche et température
            niche_data = {}
            temperature_data = {}
            
            for response in responses:
                lead_id = response.get("lead_id")
                channel = response.get("channel")
                sentiment = response.get("sentiment", "neutral")
                interest_level = response.get("interest_level", 0.5)
                
                # Rechercher le message original dans l'historique
                message_history = self._load_message_history()
                
                for message in message_history.get("messages", []):
                    if message.get("lead_id") == lead_id:
                        niche = message.get("niche", "general")
                        lead_temperature = message.get("lead_temperature", "warm")
                        
                        # Initialiser les données de niche si nécessaire
                        if niche not in niche_data:
                            niche_data[niche] = {
                                "email": {"count": 0, "success": 0},
                                "sms": {"count": 0, "success": 0}
                            }
                        
                        # Initialiser les données de température si nécessaire
                        if lead_temperature not in temperature_data:
                            temperature_data[lead_temperature] = {
                                "email": {"count": 0, "success": 0},
                                "sms": {"count": 0, "success": 0}
                            }
                        
                        # Incrémenter les compteurs
                        niche_data[niche][channel]["count"] += 1
                        temperature_data[lead_temperature][channel]["count"] += 1
                        
                        # Si la réponse est positive (sentiment positif ou intérêt élevé)
                        if sentiment == "positive" or interest_level > 0.7:
                            niche_data[niche][channel]["success"] += 1
                            temperature_data[lead_temperature][channel]["success"] += 1
            
            # Mettre à jour les statistiques par niche
            by_niche = channel_stats.get("by_niche", {})
            
            for niche, data in niche_data.items():
                if niche not in by_niche:
                    by_niche[niche] = {}
                
                for channel, stats in data.items():
                    if stats["count"] > 0:
                        by_niche[niche][channel] = stats["success"] / stats["count"]
            
            channel_stats["by_niche"] = by_niche
            
            # Mettre à jour les statistiques par température
            by_temperature = channel_stats.get("by_temperature", {})
            
            for temp, data in temperature_data.items():
                if temp not in by_temperature:
                    by_temperature[temp] = {}
                
                for channel, stats in data.items():
                    if stats["count"] > 0:
                        by_temperature[temp][channel] = stats["success"] / stats["count"]
            
            channel_stats["by_temperature"] = by_temperature
            
            # Mettre à jour la préférence globale
            global_data = {
                "email": {"count": 0, "success": 0},
                "sms": {"count": 0, "success": 0}
            }
            
            for niche_stats in niche_data.values():
                for channel, stats in niche_stats.items():
                    global_data[channel]["count"] += stats["count"]
                    global_data[channel]["success"] += stats["success"]
            
            global_preference = channel_stats.get("global_preference", {})
            
            for channel, stats in global_data.items():
                if stats["count"] > 0:
                    global_preference[channel] = stats["success"] / stats["count"]
            
            channel_stats["global_preference"] = global_preference
            
            return channel_stats
        
        except Exception as e:
            print(f"[{self.name}] ⚠️ Erreur lors de la mise à jour des statistiques par canal: {str(e)}")
            return channel_stats
    
    def _get_pending_followups(self, message_history, followup_schedule):
        """
        Récupère les suivis en attente à envoyer
        """
        try:
            now = datetime.datetime.now()
            followups_due = []
            leads_to_followup = []
            niche = "general"
            
            # Parcourir l'historique des messages pour trouver les suivis programmés
            for message in message_history.get("messages", []):
                lead_id = message.get("lead_id")
                followup = message.get("followup", {})
                is_followup = message.get("is_followup", False)
                message_niche = message.get("niche", "general")
                
                # Si ce message est déjà un suivi, le sauter
                if is_followup:
                    continue
                
                # Si le message a eu une réponse, le sauter
                if message.get("status") == "replied":
                    continue
                
                # Si des dates de suivi sont programmées
                if "followup_dates" in followup:
                    followup_dates = followup.get("followup_dates", [])
                    
                    # Vérifier s'il y a des dates de suivi passées mais non envoyées
                    for date_str in followup_dates:
                        followup_date = datetime.datetime.fromisoformat(date_str)
                        
                        # Si la date de suivi est passée
                        if followup_date <= now:
                            # Vérifier si ce suivi a déjà été envoyé
                            already_sent = False
                            
                            for sent_message in message_history.get("messages", []):
                                if (sent_message.get("lead_id") == lead_id and 
                                    sent_message.get("is_followup") and 
                                    sent_message.get("original_message_timestamp") == message.get("timestamp")):
                                    already_sent = True
                                    break
                            
                            if not already_sent:
                                # Récupérer les données du lead
                                lead_data = {
                                    "id": lead_id,
                                    "name": message.get("lead_name"),
                                    "email": message.get("lead_email"),
                                    "phone": message.get("lead_phone")
                                }
                                
                                followups_due.append({
                                    "lead_id": lead_id,
                                    "original_message_timestamp": message.get("timestamp"),
                                    "followup_date": date_str,
                                    "niche": message_niche
                                })
                                
                                leads_to_followup.append(lead_data)
                                niche = message_niche  # Utiliser la niche du dernier message
            
            if not followups_due:
                return None
            
            return {
                "followups": followups_due,
                "leads": leads_to_followup,
                "niche": niche
            }
        
        except Exception as e:
            print(f"[{self.name}] ⚠️ Erreur lors de la récupération des suivis en attente: {str(e)}")
            return None
    
    def _update_followup_schedule(self, new_schedule, current_schedule):
        """
        Met à jour le planning de suivi
        """
        try:
            updated_schedule = current_schedule.copy()
            
            # Mettre à jour le planning par défaut si fourni
            if "default" in new_schedule:
                updated_schedule["default"] = new_schedule["default"]
            
            # Mettre à jour les plannings par niche
            if "by_niche" in new_schedule:
                if "by_niche" not in updated_schedule:
                    updated_schedule["by_niche"] = {}
                
                for niche, schedule in new_schedule["by_niche"].items():
                    updated_schedule["by_niche"][niche] = schedule
            
            # Mettre à jour les plannings par température
            if "by_temperature" in new_schedule:
                if "by_temperature" not in updated_schedule:
                    updated_schedule["by_temperature"] = {}
                
                for temp, schedule in new_schedule["by_temperature"].items():
                    updated_schedule["by_temperature"][temp] = schedule
            
            return updated_schedule
        
        except Exception as e:
            print(f"[{self.name}] ⚠️ Erreur lors de la mise à jour du planning de suivi: {str(e)}")
            return current_schedule
    
    def _analyze_message_performance(self, message_history, response_stats, period, niche):
        """
        Analyse les performances des messages
        """
        try:
            # Filtrer les messages selon la période et la niche
            messages = message_history.get("messages", [])
            filtered_messages = []
            
            now = datetime.datetime.now()
            period_start = None
            
            # Déterminer la date de début selon la période
            if period == "day":
                period_start = now - datetime.timedelta(days=1)
            elif period == "week":
                period_start = now - datetime.timedelta(days=7)
            elif period == "month":
                period_start = now - datetime.timedelta(days=30)
            elif period == "quarter":
                period_start = now - datetime.timedelta(days=90)
            elif period == "year":
                period_start = now - datetime.timedelta(days=365)
            
            # Filtrer les messages
            for message in messages:
                # Filtrer par date si une période est spécifiée
                if period != "all" and period_start:
                    message_date = datetime.datetime.fromisoformat(message.get("timestamp"))
                    if message_date < period_start:
                        continue
                
                # Filtrer par niche si spécifiée
                if niche != "all" and message.get("niche") != niche:
                    continue
                
                filtered_messages.append(message)
            
            # Analyser les performances
            performance = {
                "total_messages": len(filtered_messages),
                "period": period,
                "niche": niche,
                "by_channel": {
                    "email": {
                        "sent": 0,
                        "delivered": 0,
                        "opened": 0,
                        "clicked": 0,
                        "replied": 0,
                        "response_rate": 0.0
                    },
                    "sms": {
                        "sent": 0,
                        "delivered": 0,
                        "replied": 0,
                        "response_rate": 0.0
                    },
                    "both": {
                        "sent": 0,
                        "replied": 0,
                        "response_rate": 0.0
                    }
                },
                "by_temperature": {
                    "hot": {"sent": 0, "replied": 0, "response_rate": 0.0},
                    "warm": {"sent": 0, "replied": 0, "response_rate": 0.0},
                    "cold": {"sent": 0, "replied": 0, "response_rate": 0.0}
                },
                "followup_effectiveness": {
                    "initial": {"sent": 0, "replied": 0, "response_rate": 0.0},
                    "followup1": {"sent": 0, "replied": 0, "response_rate": 0.0},
                    "followup2": {"sent": 0, "replied": 0, "response_rate": 0.0},
                    "followup3+": {"sent": 0, "replied": 0, "response_rate": 0.0}
                },
                "best_performing_templates": [],
                "worst_performing_templates": [],
                "insights": []
            }
            
            # Calculer les statistiques de base
            for message in filtered_messages:
                channel = message.get("channel")
                is_followup = message.get("is_followup", False)
                status = message.get("status", "sent")
                
                # Comptabiliser par canal
                if channel in ["email", "sms", "both"]:
                    performance["by_channel"][channel]["sent"] += 1
                    
                    if status == "replied":
                        performance["by_channel"][channel]["replied"] += 1
                
                # Comptabiliser par température (si disponible)
                temperature = message.get("lead_temperature", "unknown")
                if temperature in ["hot", "warm", "cold"]:
                    performance["by_temperature"][temperature]["sent"] += 1
                    
                    if status == "replied":
                        performance["by_temperature"][temperature]["replied"] += 1
                
                # Comptabiliser par type de suivi
                if not is_followup:
                    performance["followup_effectiveness"]["initial"]["sent"] += 1
                    
                    if status == "replied":
                        performance["followup_effectiveness"]["initial"]["replied"] += 1
                else:
                    followup_number = message.get("followup_number", 1)
                    
                    if followup_number == 1:
                        category = "followup1"
                    elif followup_number == 2:
                        category = "followup2"
                    else:
                        category = "followup3+"
                    
                    performance["followup_effectiveness"][category]["sent"] += 1
                    
                    if status == "replied":
                        performance["followup_effectiveness"][category]["replied"] += 1
            
            # Calculer les taux de réponse
            for channel, stats in performance["by_channel"].items():
                if stats["sent"] > 0:
                    stats["response_rate"] = stats["replied"] / stats["sent"]
            
            for temp, stats in performance["by_temperature"].items():
                if stats["sent"] > 0:
                    stats["response_rate"] = stats["replied"] / stats["sent"]
            
            for followup_type, stats in performance["followup_effectiveness"].items():
                if stats["sent"] > 0:
                    stats["response_rate"] = stats["replied"] / stats["sent"]
            
            # Générer des insights
            insights = []
            
            # Insight sur le canal le plus efficace
            best_channel = max(performance["by_channel"].items(), key=lambda x: x[1]["response_rate"] if x[1]["sent"] > 0 else 0)
            insights.append(f"Le canal le plus efficace est {best_channel[0]} avec un taux de réponse de {best_channel[1]['response_rate']*100:.1f}%")
            
            # Insight sur l'efficacité des suivis
            initial_rate = performance["followup_effectiveness"]["initial"]["response_rate"]
            followup1_rate = performance["followup_effectiveness"]["followup1"]["response_rate"]
            
            if followup1_rate > 0:
                followup_impact = (followup1_rate - initial_rate) / initial_rate if initial_rate > 0 else 0
                insights.append(f"Les premiers suivis {'augmentent' if followup_impact > 0 else 'diminuent'} le taux de réponse de {abs(followup_impact)*100:.1f}%")
            
            # Insight sur les températures
            best_temp = max(performance["by_temperature"].items(), key=lambda x: x[1]["response_rate"] if x[1]["sent"] > 0 else 0)
            insights.append(f"Les leads {best_temp[0]} ont le meilleur taux de réponse ({best_temp[1]['response_rate']*100:.1f}%)")
            
            performance["insights"] = insights
            
            return performance
        
        except Exception as e:
            print(f"[{self.name}] ⚠️ Erreur lors de l'analyse des performances: {str(e)}")
            return {"error": str(e)}
