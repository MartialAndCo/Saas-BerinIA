from datetime import datetime, timedelta
import time
import json
import re
from typing import Dict, Any, List, Optional
import logging
import html

from .base import BaseAgent
from .utils.llm import ask_llm, generate_structured_response

class MessengerAgent(BaseAgent):
    """
    Agent responsable de la génération et de l'envoi de messages personnalisés.
    
    Cet agent crée des messages personnalisés adaptés à chaque lead
    et les envoie via différents canaux (email, SMS, etc.).
    """
    
    def __init__(self, agent_id, db_session):
        super().__init__(agent_id, db_session)
        # Charger la configuration des canaux d'envoi
        self.channel_configs = {}
        if self.agent_model and self.agent_model.configuration:
            self.channel_configs = self.agent_model.configuration.get("channels", {})
    
    def run(self, input_data):
        """
        Exécute l'agent de messagerie.
        
        Args:
            input_data (dict): Les données d'entrée, qui peuvent inclure:
                - leads: Liste des leads à contacter
                - campaign_id: ID de la campagne
                - template_id: ID du template de message (optionnel)
                - template_content: Contenu du template (si template_id non fourni)
                - channel: Canal d'envoi (email, sms, etc.)
                - personalization_level: Niveau de personnalisation (basic, advanced, custom)
                - scheduled_time: Heure planifiée pour l'envoi (optionnel)
                
        Returns:
            dict: Résultats de l'exécution
        """
        self.logger.info(f"Lancement de MessengerAgent pour {len(input_data.get('leads', []))} leads")
        
        start_time = time.time()
        
        try:
            # Extraire les paramètres
            leads = input_data.get('leads', [])
            campaign_id = input_data.get('campaign_id')
            template_id = input_data.get('template_id')
            template_content = input_data.get('template_content')
            channel = input_data.get('channel', 'email')
            personalization_level = input_data.get('personalization_level', 'basic')
            scheduled_time = input_data.get('scheduled_time')
            
            if not leads:
                return {
                    'status': 'error',
                    'message': 'Aucun lead à contacter',
                    'messages_sent': 0
                }
            
            # Récupérer le template si ID fourni
            template = None
            if template_id:
                template = self._get_template(template_id)
                if template:
                    template_content = template.get('content')
            
            # Vérifier si le contenu du template est disponible
            if not template_content:
                return {
                    'status': 'error',
                    'message': 'Aucun contenu de template disponible',
                    'messages_sent': 0
                }
            
            # Récupérer les informations de campagne si nécessaire pour la personnalisation avancée
            campaign_info = None
            if personalization_level in ['advanced', 'custom'] and campaign_id:
                campaign_info = self._get_campaign_info(campaign_id)
            
            # Préparer et envoyer les messages
            sent_messages = []
            failed_messages = []
            
            for lead in leads:
                try:
                    # Génération du message personnalisé
                    message = self._generate_message(
                        lead=lead,
                        template_content=template_content,
                        campaign_info=campaign_info,
                        personalization_level=personalization_level,
                        channel=channel
                    )
                    
                    # Envoi du message
                    message_result = self._send_message(
                        lead=lead,
                        message=message,
                        channel=channel,
                        scheduled_time=scheduled_time
                    )
                    
                    # Enregistrer le résultat
                    if message_result.get('status') == 'success':
                        message_record = {
                            'lead': lead,
                            'message': message,
                            'channel': channel,
                            'sent_at': message_result.get('sent_at', datetime.utcnow().isoformat()),
                            'message_id': message_result.get('message_id')
                        }
                        sent_messages.append(message_record)
                    else:
                        failed_messages.append({
                            'lead': lead,
                            'error': message_result.get('error'),
                            'channel': channel
                        })
                        
                except Exception as e:
                    self.logger.error(f"Erreur lors de l'envoi au lead {lead.get('email', 'unknown')}: {str(e)}")
                    failed_messages.append({
                        'lead': lead,
                        'error': str(e),
                        'channel': channel
                    })
            
            # Enregistrer les messages envoyés dans la base de données
            if campaign_id and sent_messages:
                self._save_sent_messages(sent_messages, campaign_id, template_id)
            
            execution_time = time.time() - start_time
            
            # Préparer les résultats
            results = {
                'status': 'success',
                'message': f"{len(sent_messages)} messages envoyés, {len(failed_messages)} échecs",
                'messages_sent': len(sent_messages),
                'messages_failed': len(failed_messages),
                'sent_messages': sent_messages,
                'failed_messages': failed_messages,
                'execution_time': execution_time
            }
            
            # Logging des résultats
            self.log_execution(
                operation=f"send_messages_{channel}",
                input_data={'lead_count': len(leads), 'campaign_id': campaign_id, 'template_id': template_id},
                output_data=results,
                status="success" if not failed_messages else "partial_success",
                execution_time=execution_time
            )
            
            return results
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Erreur lors de l'exécution de MessengerAgent: {str(e)}")
            
            # Logging de l'erreur
            self.log_execution(
                operation=f"send_messages_{input_data.get('channel', 'unknown')}",
                input_data=input_data,
                output_data={"error": str(e)},
                status="error",
                execution_time=execution_time
            )
            
            return {
                'status': 'error',
                'message': str(e),
                'messages_sent': 0
            }
    
    def _get_template(self, template_id):
        """
        Récupère un template de message par ID.
        
        Args:
            template_id: ID du template
            
        Returns:
            dict: Données du template
        """
        try:
            # Récupérer le template
            template = self.db.query(MessageTemplateModel).filter(
                MessageTemplateModel.id == template_id
            ).first()
            
            if not template:
                self.logger.error(f"Template avec ID {template_id} non trouvé")
                return None
            
            # Convertir en dictionnaire
            template_dict = {
                'id': template.id,
                'name': template.name,
                'type': template.type,
                'content': template.content,
                'variables': template.variables,
                'created_at': template.created_at.isoformat() if template.created_at else None,
                'updated_at': template.updated_at.isoformat() if template.updated_at else None
            }
            
            return template_dict
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération du template: {str(e)}")
            return None
    
    def _get_campaign_info(self, campaign_id):
        """
        Récupère les informations de la campagne pour personnalisation.
        
        Args:
            campaign_id: ID de la campagne
            
        Returns:
            dict: Informations de la campagne
        """
        try:
            # Récupérer la campagne
            campaign = self.db.query(CampaignModel).filter(
                CampaignModel.id == campaign_id
            ).first()
            
            if not campaign:
                self.logger.error(f"Campagne avec ID {campaign_id} non trouvée")
                return {}
            
            # Récupérer les données additionnelles
            niche = self.db.query(NicheModel).filter(
                NicheModel.id == campaign.niche_id
            ).first() if campaign.niche_id else None
            
            # Assembler les informations
            campaign_info = {
                'id': campaign.id,
                'name': campaign.name,
                'description': campaign.description,
                'niche': niche.name if niche else campaign.niche,
                'target_audience': campaign.target_audience,
                'value_proposition': campaign.value_proposition,
                'main_benefits': campaign.main_benefits,
                'start_date': campaign.start_date.isoformat() if campaign.start_date else None,
                'sender_name': campaign.sender_name,
                'sender_email': campaign.sender_email,
                'company_name': campaign.company_name,
                'company_website': campaign.company_website
            }
            
            return campaign_info
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des informations de campagne: {str(e)}")
            return {}
    
    def _generate_message(self, lead, template_content, campaign_info, personalization_level, channel):
        """
        Génère un message personnalisé pour un lead.
        
        Args:
            lead: Données du lead
            template_content: Contenu du template
            campaign_info: Informations de la campagne
            personalization_level: Niveau de personnalisation
            channel: Canal de communication
            
        Returns:
            dict: Message personnalisé
        """
        if personalization_level == 'basic':
            # Personnalisation basique par remplacement de variables
            return self._basic_personalization(lead, template_content, campaign_info, channel)
        elif personalization_level == 'advanced':
            # Personnalisation avancée avec génération de contenu
            return self._advanced_personalization(lead, template_content, campaign_info, channel)
        elif personalization_level == 'custom':
            # Personnalisation complète avec LLM
            return self._custom_personalization(lead, template_content, campaign_info, channel)
        else:
            # Par défaut, personnalisation basique
            return self._basic_personalization(lead, template_content, campaign_info, channel)
    
    def _basic_personalization(self, lead, template_content, campaign_info, channel):
        """
        Personnalisation basique par remplacement de variables.
        
        Args:
            lead: Données du lead
            template_content: Contenu du template
            campaign_info: Informations de la campagne
            channel: Canal de communication
            
        Returns:
            dict: Message personnalisé
        """
        # Créer un dictionnaire combiné pour le remplacement de variables
        variables = {}
        
        # Variables du lead
        if lead:
            variables.update({
                "first_name": lead.get("first_name", ""),
                "last_name": lead.get("last_name", ""),
                "full_name": f"{lead.get('first_name', '')} {lead.get('last_name', '')}".strip(),
                "email": lead.get("email", ""),
                "company": lead.get("company", ""),
                "job_title": lead.get("job_title", ""),
                "phone": lead.get("phone", ""),
                "city": lead.get("city", ""),
                "country": lead.get("country", "")
            })
        
        # Variables de la campagne
        if campaign_info:
            variables.update({
                "campaign_name": campaign_info.get("name", ""),
                "niche": campaign_info.get("niche", ""),
                "company_name": campaign_info.get("company_name", ""),
                "company_website": campaign_info.get("company_website", ""),
                "sender_name": campaign_info.get("sender_name", ""),
                "sender_email": campaign_info.get("sender_email", ""),
                "value_proposition": campaign_info.get("value_proposition", ""),
                "main_benefits": campaign_info.get("main_benefits", "")
            })
        
        # Personnaliser le contenu
        personalized_content = template_content
        
        # Remplacer les variables dans le format {{variable}}
        for key, value in variables.items():
            if value:  # Vérifier que la valeur n'est pas vide
                personalized_content = personalized_content.replace(f"{{{{{key}}}}}", str(value))
        
        # Nettoyer les variables non remplacées
        personalized_content = re.sub(r'\{\{[^}]+\}\}', '', personalized_content)
        
        # Préparer le message en fonction du canal
        message = self._format_message_for_channel(personalized_content, lead, campaign_info, channel)
        
        return message
    
    def _advanced_personalization(self, lead, template_content, campaign_info, channel):
        """
        Personnalisation avancée avec génération de contenu.
        
        Args:
            lead: Données du lead
            template_content: Contenu du template
            campaign_info: Informations de la campagne
            channel: Canal de communication
            
        Returns:
            dict: Message personnalisé
        """
        # Commencer par la personnalisation basique
        personalized_content = self._basic_personalization(lead, template_content, campaign_info, channel)
        
        # Utiliser des patterns spéciaux pour demander la génération de contenu
        generate_patterns = re.finditer(r'\[\[GENERATE:(.*?)\]\]', personalized_content['content'])
        
        for match in generate_patterns:
            generation_instruction = match.group(1).strip()
            
            # Générer le contenu selon l'instruction
            generated_content = self._generate_content_segment(generation_instruction, lead, campaign_info)
            
            # Remplacer l'instruction par le contenu généré
            personalized_content['content'] = personalized_content['content'].replace(match.group(0), generated_content)
        
        return personalized_content
    
    def _generate_content_segment(self, instruction, lead, campaign_info):
        """
        Génère un segment de contenu selon l'instruction.
        
        Args:
            instruction: Instruction de génération
            lead: Données du lead
            campaign_info: Informations de la campagne
            
        Returns:
            str: Segment de contenu généré
        """
        prompt = f"""
        Génère un court segment de contenu pour un email commercial selon cette instruction:
        "{instruction}"
        
        Contexte sur le destinataire:
        - Nom: {lead.get('first_name', '')} {lead.get('last_name', '')}
        - Entreprise: {lead.get('company', '')}
        - Poste: {lead.get('job_title', '')}
        
        Contexte sur l'offre:
        - Entreprise expéditrice: {campaign_info.get('company_name', '')}
        - Niche: {campaign_info.get('niche', '')}
        - Proposition de valeur: {campaign_info.get('value_proposition', '')}
        
        Le segment doit:
        - Être concis et professionnel
        - Ne pas dépasser 3 phrases
        - S'intégrer naturellement dans un email
        - Ne pas inclure de formules d'introduction/conclusion
        """
        
        response = ask_llm(
            prompt=prompt,
            system_message="Tu es un expert en copywriting qui génère des segments de contenu persuasifs et professionnels pour des emails commerciaux.",
            max_tokens=150
        )
        
        return response.get('text', '')
    
    def _custom_personalization(self, lead, template_content, campaign_info, channel):
        """
        Personnalisation complète avec LLM.
        
        Args:
            lead: Données du lead
            template_content: Contenu du template (utilisé comme guide)
            campaign_info: Informations de la campagne
            channel: Canal de communication
            
        Returns:
            dict: Message personnalisé
        """
        # Structure du schéma pour le message personnalisé
        message_schema = {
            "message": {
                "subject": "Ligne d'objet personnalisée",
                "body": "Corps du message personnalisé",
                "personalization_notes": ["Explication 1", "Explication 2"]
            }
        }
        
        # Convertir les données en format texte pour le prompt
        lead_text = "\n".join([f"- {k}: {v}" for k, v in lead.items() if v and k not in ['id', 'campaign_id']])
        campaign_text = "\n".join([f"- {k}: {v}" for k, v in campaign_info.items() if v and k not in ['id']])
        
        # Extraire le sujet du template s'il est fourni dans un format structuré
        template_subject = ""
        if isinstance(template_content, dict) and 'subject' in template_content:
            template_subject = template_content['subject']
            template_body = template_content['content']
        else:
            # Essayer de détecter un sujet dans le template texte
            match = re.search(r'^Subject:\s*(.+)$', template_content, re.MULTILINE)
            if match:
                template_subject = match.group(1)
                template_body = re.sub(r'^Subject:\s*.+$\n', '', template_content, flags=re.MULTILINE)
            else:
                template_body = template_content
        
        # Construire le prompt
        prompt = f"""
        En tant qu'expert en communication personnalisée, rédige un message entièrement personnalisé pour ce lead spécifique.
        
        DÉTAILS DU LEAD:
        {lead_text}
        
        CONTEXTE DE LA CAMPAGNE:
        {campaign_text}
        
        TEMPLATE COMME GUIDE:
        Sujet: {template_subject}
        
        Corps:
        {template_body}
        
        INSTRUCTIONS:
        1. Crée un message parfaitement adapté à ce lead en fonction de son entreprise, son poste, et son secteur
        2. Le message doit être professionnel, concis et percutant
        3. Adapte la proposition de valeur pour répondre aux besoins spécifiques probables de ce lead
        4. Crée une ligne d'objet unique et personnalisée pour maximiser l'ouverture
        5. Inclus au moins 2-3 points de personnalisation spécifiques à ce lead
        
        Si le canal est "{channel}", adapte le style et la longueur en conséquence.
        """
        
        # Générer le message personnalisé
        response = generate_structured_response(
            prompt=prompt,
            schema=message_schema,
            system_message="Tu es un expert en copywriting et communication personnalisée qui crée des messages parfaitement adaptés à chaque destinataire.",
            model="gpt-4.1"
        )
        
        if "message" in response:
            message = response["message"]
            
            # Préparer le message en fonction du canal
            formatted_message = {
                "subject": message.get("subject", ""),
                "content": message.get("body", ""),
                "personalization_notes": message.get("personalization_notes", [])
            }
            
            return self._format_message_for_channel(formatted_message, lead, campaign_info, channel)
        else:
            # Fallback à la personnalisation avancée en cas d'échec
            self.logger.warning("Échec de la personnalisation LLM, fallback à la personnalisation avancée")
            return self._advanced_personalization(lead, template_content, campaign_info, channel)
    
    def _format_message_for_channel(self, content, lead, campaign_info, channel):
        """
        Formate le message pour le canal spécifique.
        
        Args:
            content: Contenu du message
            lead: Données du lead
            campaign_info: Informations de la campagne
            channel: Canal de communication
            
        Returns:
            dict: Message formaté
        """
        # Si le contenu est déjà un dictionnaire structuré
        if isinstance(content, dict):
            message = content
            # S'assurer que le format est correct
            if "subject" not in message and channel == "email":
                message["subject"] = campaign_info.get("value_proposition", "")
        else:
            # Si le contenu est une chaîne
            message = {}
            if channel == "email":
                # Essayer d'extraire le sujet
                match = re.search(r'^Subject:\s*(.+)$', content, re.MULTILINE)
                if match:
                    message["subject"] = match.group(1)
                    message["content"] = re.sub(r'^Subject:\s*.+$\n', '', content, flags=re.MULTILINE)
                else:
                    message["subject"] = campaign_info.get("value_proposition", "")
                    message["content"] = content
            else:
                message["content"] = content
        
        # Adaptations spécifiques au canal
        if channel == "email":
            # Vérifier la longueur et le format HTML pour l'email
            if len(message["content"]) > 5000:
                message["content"] = message["content"][:4997] + "..."
            
            # Convertir en HTML si le contenu n'est pas déjà en HTML
            if "<html" not in message["content"] and "<body" not in message["content"]:
                message["content"] = self._text_to_html(message["content"], campaign_info)
                
        elif channel == "sms":
            # Limites pour les SMS
            if len(message["content"]) > 160:
                message["content"] = message["content"][:157] + "..."
                
        # Ajouter des métadonnées
        message["channel"] = channel
        message["recipient"] = {
            "name": f"{lead.get('first_name', '')} {lead.get('last_name', '')}".strip(),
            "email": lead.get("email", ""),
            "phone": lead.get("phone", "")
        }
        
        if campaign_info:
            message["sender"] = {
                "name": campaign_info.get("sender_name", ""),
                "email": campaign_info.get("sender_email", ""),
                "company": campaign_info.get("company_name", "")
            }
        
        return message
    
    def _text_to_html(self, text, campaign_info):
        """
        Convertit un texte brut en HTML pour le format email.
        
        Args:
            text: Texte à convertir
            campaign_info: Informations de la campagne pour la signature
            
        Returns:
            str: Version HTML du message
        """
        # Échapper le HTML
        escaped_text = html.escape(text)
        
        # Convertir les sauts de ligne en balises <p>
        paragraphs = [f"<p>{p.strip()}</p>" for p in escaped_text.split("\n\n") if p.strip()]
        body_html = "\n".join(paragraphs)
        
        # Créer une signature si les informations sont disponibles
        signature = ""
        if campaign_info:
            sender_name = campaign_info.get("sender_name", "")
            company_name = campaign_info.get("company_name", "")
            company_website = campaign_info.get("company_website", "")
            
            if sender_name or company_name:
                signature = f"""
                <div style="margin-top: 20px; border-top: 1px solid #ddd; padding-top: 10px; color: #666;">
                    <p><strong>{sender_name}</strong><br>
                    {company_name}</p>
                """
                
                if company_website:
                    signature += f'<p><a href="{company_website}">{company_website}</a></p>'
                    
                signature += "</div>"
        
        # Construire le document HTML complet
        html_email = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; }}
                p {{ margin-bottom: 16px; }}
                a {{ color: #0066cc; }}
            </style>
        </head>
        <body>
            {body_html}
            {signature}
        </body>
        </html>
        """
        
        return html_email
    
    def _send_message(self, lead, message, channel, scheduled_time=None):
        """
        Envoie le message via le canal spécifié.
        
        Args:
            lead: Données du lead
            message: Message à envoyer
            channel: Canal d'envoi
            scheduled_time: Heure planifiée pour l'envoi
            
        Returns:
            dict: Résultat de l'envoi
        """
        # Vérifier que l'envoi est bien configuré
        if channel not in self.channel_configs:
            return {
                'status': 'error',
                'error': f"Canal {channel} non configuré"
            }
        
        # Si un temps est planifié et qu'il est dans le futur
        now = datetime.utcnow()
        if scheduled_time:
            scheduled_dt = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
            if scheduled_dt > now:
                # Enregistrer pour envoi ultérieur
                return self._schedule_message(lead, message, channel, scheduled_dt)
        
        # Envoi immédiat selon le canal
        if channel == 'email':
            return self._send_email(lead, message)
        elif channel == 'sms':
            return self._send_sms(lead, message)
        else:
            return {
                'status': 'error',
                'error': f"Canal {channel} non supporté"
            }
    
    def _send_email(self, lead, message):
        """
        Envoie un email.
        
        Args:
            lead: Données du lead
            message: Message à envoyer
            
        Returns:
            dict: Résultat de l'envoi
        """
        try:
            # Récupérer la configuration email
            email_config = self.channel_configs.get('email', {})
            provider = email_config.get('provider', 'smtp')
            
            if provider == 'smtp':
                # Implémentation d'envoi SMTP
                from email.mime.multipart import MIMEMultipart
                from email.mime.text import MIMEText
                import smtplib
                
                # Créer le message
                msg = MIMEMultipart('alternative')
                msg['Subject'] = message.get('subject', '')
                msg['From'] = message.get('sender', {}).get('email', email_config.get('default_from', ''))
                msg['To'] = lead.get('email', '')
                
                # Ajouter le contenu
                msg.attach(MIMEText(message.get('content', ''), 'html'))
                
                # Configurer le serveur SMTP
                server = smtplib.SMTP(
                    email_config.get('smtp_server', 'localhost'), 
                    email_config.get('smtp_port', 25)
                )
                
                if email_config.get('use_tls', False):
                    server.starttls()
                
                # Authentification si nécessaire
                if email_config.get('smtp_user') and email_config.get('smtp_password'):
                    server.login(email_config.get('smtp_user'), email_config.get('smtp_password'))
                
                # Envoi
                server.send_message(msg)
                server.quit()
                
                return {
                    'status': 'success',
                    'sent_at': datetime.utcnow().isoformat(),
                    'message_id': f"email_{int(time.time())}_{lead.get('id', '')}"
                }
                
            elif provider == 'api':
                # Simulation d'appel API
                self.logger.info(f"Simulation d'envoi d'email via API à {lead.get('email')}")
                
                return {
                    'status': 'success',
                    'sent_at': datetime.utcnow().isoformat(),
                    'message_id': f"email_api_{int(time.time())}_{lead.get('id', '')}"
                }
            
            else:
                # Simulation d'envoi pour les tests
                self.logger.info(f"Simulation d'envoi d'email à {lead.get('email')}")
                
                return {
                    'status': 'success',
                    'sent_at': datetime.utcnow().isoformat(),
                    'message_id': f"email_sim_{int(time.time())}_{lead.get('id', '')}"
                }
                
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi d'email: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _send_sms(self, lead, message):
        """
        Envoie un SMS.
        
        Args:
            lead: Données du lead
            message: Message à envoyer
            
        Returns:
            dict: Résultat de l'envoi
        """
        try:
            # Récupérer la configuration SMS
            sms_config = self.channel_configs.get('sms', {})
            provider = sms_config.get('provider', 'simulation')
            
            if provider == 'twilio':
                # Implémentation Twilio serait ici
                self.logger.info(f"Envoi SMS via Twilio à {lead.get('phone')}")
                
                return {
                    'status': 'success',
                    'sent_at': datetime.utcnow().isoformat(),
                    'message_id': f"sms_twilio_{int(time.time())}_{lead.get('id', '')}"
                }
                
            else:
                # Simulation d'envoi pour les tests
                self.logger.info(f"Simulation d'envoi de SMS à {lead.get('phone')}")
                
                return {
                    'status': 'success',
                    'sent_at': datetime.utcnow().isoformat(),
                    'message_id': f"sms_sim_{int(time.time())}_{lead.get('id', '')}"
                }
                
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi de SMS: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _schedule_message(self, lead, message, channel, scheduled_time):
        """
        Programme un message pour envoi ultérieur.
        
        Args:
            lead: Données du lead
            message: Message à envoyer
            channel: Canal d'envoi
            scheduled_time: Heure planifiée pour l'envoi
            
        Returns:
            dict: Résultat de la programmation
        """
        try:
            # Créer l'entrée de programmation
            scheduled_message = ScheduledMessageModel(
                lead_id=lead.get('id'),
                channel=channel,
                content=json.dumps(message),
                scheduled_time=scheduled_time,
                status='pending',
                created_at=datetime.utcnow()
            )
            
            self.db.add(scheduled_message)
            self.db.commit()
            
            self.logger.info(f"Message programmé pour {scheduled_time.isoformat()} via {channel}")
            
            return {
                'status': 'success',
                'scheduled_at': scheduled_time.isoformat(),
                'message_id': f"scheduled_{scheduled_message.id}"
            }
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la programmation du message: {str(e)}")
            self.db.rollback()
            
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _save_sent_messages(self, sent_messages, campaign_id, template_id=None):
        """
        Enregistre les messages envoyés dans la base de données.
        
        Args:
            sent_messages: Liste des messages envoyés
            campaign_id: ID de la campagne
            template_id: ID du template utilisé (optionnel)
        """
        try:
            # Préparer les données pour l'insertion
            message_records = []
            for message_data in sent_messages:
                lead = message_data.get('lead', {})
                message = message_data.get('message', {})
                
                record = {
                    'lead_id': lead.get('id'),
                    'campaign_id': campaign_id,
                    'template_id': template_id,
                    'channel': message_data.get('channel', 'email'),
                    'subject': message.get('subject', ''),
                    'content': json.dumps(message.get('content', '')),
                    'sent_at': datetime.fromisoformat(message_data.get('sent_at').replace('Z', '+00:00')) 
                              if isinstance(message_data.get('sent_at'), str) else datetime.utcnow(),
                    'status': 'sent',
                    'message_id': message_data.get('message_id', '')
                }
                
                message_records.append(record)
            
            # Insérer en masse
            if message_records:
                self.db.execute(SentMessageModel.__table__.insert(), message_records)
                self.db.commit()
                
                self.logger.info(f"{len(message_records)} messages enregistrés pour la campagne {campaign_id}")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'enregistrement des messages: {str(e)}")
            self.db.rollback()
    
    def store_feedback(self, message_id, feedback):
        """
        Stocke le feedback sur un message envoyé.
        
        Args:
            message_id: ID du message
            feedback: Données de feedback
            
        Returns:
            bool: Succès de l'opération
        """
        try:
            # Récupérer le message
            message = self.db.query(SentMessageModel).filter(
                SentMessageModel.id == message_id
            ).first()
            
            if not message:
                self.logger.error(f"Message avec ID {message_id} non trouvé")
                return False
            
            # Mettre à jour avec le feedback
            message.feedback_score = feedback.get('score')
            message.feedback_text = feedback.get('text')
            message.feedback_timestamp = datetime.utcnow()
            
            # Si le lead a interagi avec le message
            if 'interaction' in feedback:
                message.interaction_type = feedback['interaction'].get('type', '')
                message.interaction_timestamp = feedback['interaction'].get('timestamp', datetime.utcnow())
                message.interaction_data = json.dumps(feedback['interaction'].get('data', {}))
            
            self.db.commit()
            
            # Log le feedback
            self.logger.info(f"Feedback enregistré pour le message {message_id}: Score {feedback.get('score')}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors du stockage du feedback: {str(e)}")
            self.db.rollback()
            return False
