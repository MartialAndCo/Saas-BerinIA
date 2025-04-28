from agents.base.base import AgentBase
from utils.llm import ask_gpt_4_1
from logs.agent_logger import log_agent
import json
import datetime
import os
import re

class LeadClassifierAgent(AgentBase):
    def __init__(self):
        super().__init__("LeadClassifierAgent")
        self.prompt_path = "prompts/lead_classifier_agent_prompt.txt"
        self.scoring_config_path = "config/scoring_config.json"
        self.heuristics_path = "config/business_heuristics.json"
        self.feedback_history_path = "logs/crm_feedback_history.json"
        self.learning_cache_path = "logs/classifier_learning.json"
        self._ensure_files_exist()
    
    def _ensure_files_exist(self):
        """Ensures that necessary files for lead classification exist"""
        # Scoring configuration
        if not os.path.exists(self.scoring_config_path):
            default_scoring = {
                "email": {
                    "pattern_weight": 0.4,
                    "domain_weight": 0.3,
                    "length_weight": 0.2,
                    "special_chars_weight": 0.1,
                    "domain_scores": {
                        "gmail.com": 0.7,
                        "yahoo.com": 0.6,
                        "hotmail.com": 0.6,
                        "outlook.com": 0.6,
                        "aol.com": 0.5,
                        "professional_domains": 0.9,
                        "other": 0.4
                    }
                },
                "phone": {
                    "pattern_weight": 0.5,
                    "length_weight": 0.3,
                    "prefix_weight": 0.2,
                    "country_codes": {
                        "france": ["33", "+33"],
                        "belgium": ["32", "+32"],
                        "switzerland": ["41", "+41"]
                    }
                },
                "profile": {
                    "completeness_weight": 0.4,
                    "relevance_weight": 0.6,
                    "required_fields": ["name", "email", "phone", "company"],
                    "optional_fields": ["position", "industry", "website", "address"]
                },
                "global_weights": {
                    "email_weight": 0.3,
                    "phone_weight": 0.3,
                    "profile_weight": 0.4
                },
                "temperature_thresholds": {
                    "cold": 0.4,
                    "warm": 0.7,
                    "hot": 0.85
                },
                "last_updated": datetime.datetime.now().isoformat()
            }
            
            os.makedirs(os.path.dirname(self.scoring_config_path), exist_ok=True)
            with open(self.scoring_config_path, "w") as f:
                json.dump(default_scoring, f, indent=2)
        
        # Business heuristics
        if not os.path.exists(self.heuristics_path):
            default_heuristics = {
                "industry_priority": {
                    "healthcare": 0.9,
                    "technology": 0.85,
                    "finance": 0.8,
                    "retail": 0.75,
                    "manufacturing": 0.7,
                    "default": 0.5
                },
                "position_priority": {
                    "C-level": 0.95,
                    "Director": 0.85,
                    "Manager": 0.75,
                    "Specialist": 0.6,
                    "default": 0.5
                },
                "company_size_priority": {
                    "enterprise": 0.9,
                    "mid-market": 0.8,
                    "small": 0.7,
                    "startup": 0.6,
                    "default": 0.5
                },
                "location_priority": {
                    "Paris": 0.9,
                    "Lyon": 0.85,
                    "Marseille": 0.8,
                    "Bordeaux": 0.75,
                    "default": 0.6
                },
                "last_updated": datetime.datetime.now().isoformat()
            }
            
            os.makedirs(os.path.dirname(self.heuristics_path), exist_ok=True)
            with open(self.heuristics_path, "w") as f:
                json.dump(default_heuristics, f, indent=2)
        
        # CRM feedback history
        if not os.path.exists(self.feedback_history_path):
            default_feedback = {
                "feedback_entries": [],
                "aggregated_stats": {
                    "true_positives": 0,
                    "false_positives": 0,
                    "true_negatives": 0,
                    "false_negatives": 0,
                    "precision": 0,
                    "recall": 0,
                    "f1_score": 0
                },
                "model_adjustments": [],
                "last_updated": datetime.datetime.now().isoformat()
            }
            
            os.makedirs(os.path.dirname(self.feedback_history_path), exist_ok=True)
            with open(self.feedback_history_path, "w") as f:
                json.dump(default_feedback, f, indent=2)
        
        # Learning cache
        if not os.path.exists(self.learning_cache_path):
            default_learning = {
                "learned_patterns": {
                    "email": {},
                    "phone": {},
                    "profile": {}
                },
                "adjustment_factors": {
                    "email": 1.0,
                    "phone": 1.0,
                    "profile": 1.0
                },
                "successful_classifications": [],
                "misclassifications": [],
                "last_learning_update": datetime.datetime.now().isoformat()
            }
            
            os.makedirs(os.path.dirname(self.learning_cache_path), exist_ok=True)
            with open(self.learning_cache_path, "w") as f:
                json.dump(default_learning, f, indent=2)
    
    def run(self, input_data: dict) -> dict:
        print(f"[{self.name}] 🧠 Classification des leads en cours...")
        
        # Extraire les paramètres d'entrée
        operation = input_data.get("operation", "classify")
        clean_leads = input_data.get("clean_leads", [])  # Changé de 'leads' à 'clean_leads' pour correspondre à l'API de CampaignStarterAgent
        campaign_id = input_data.get("campaign_id", None)
        extra_context = input_data.get("context", {})
        
        # Préparer le résultat
        result = {
            "operation": operation,
            "campaign_id": campaign_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "status": "PROCESSING"
        }
        
        try:
            # Charger les configurations nécessaires
            scoring_config = self._load_scoring_config()
            business_heuristics = self._load_business_heuristics()
            feedback_history = self._load_crm_feedback()
            learning_cache = self._load_learning_cache()
            
            # Exécuter l'opération demandée
            if operation == "classify":
                # Utiliser clean_leads comme source de leads
                leads = clean_leads
                
                # Classifier les leads si disponibles, sinon renvoyer un résultat vide mais valide
                if not leads:
                    # Au lieu d'échouer, retourner un résultat vide mais valide
                    result["classified_leads"] = []
                    result["metrics"] = {
                        "total_leads": 0,
                        "avg_global_score": 0,
                        "valid_contacts": 0
                    }
                    result["message"] = "Aucun lead fourni pour la classification. Prêt pour la prochaine série de leads."
                    result["status"] = "COMPLETED"  # Remplacer FAILED par COMPLETED pour éviter les erreurs
                    log_agent(self.name, input_data, result)
                    return result
                
                # Préparer les données pour la classification
                classification_data = self._prepare_classification_data(
                    leads, 
                    scoring_config, 
                    business_heuristics, 
                    learning_cache, 
                    extra_context
                )
                
                # Charger le prompt
                try:
                    with open(self.prompt_path, "r") as file:
                        prompt_template = file.read()
                except Exception as e:
                    result["error"] = f"Erreur lors du chargement du prompt: {str(e)}"
                    result["status"] = "FAILED"
                    log_agent(self.name, input_data, result)
                    return result
                
                # Construire le prompt pour la classification
                prompt = prompt_template.replace("{{operation}}", operation)
                prompt = prompt.replace("{{classification_data}}", json.dumps(classification_data, ensure_ascii=False))
                
                # Appliquer d'abord les heuristiques basées sur les règles métier
                scored_leads = self._apply_business_heuristics(leads, business_heuristics)
                
                # Calculer les scores détaillés
                detailed_scores = self._calculate_detailed_scores(scored_leads, scoring_config, learning_cache)
                
                # Enrichir avec GPT pour les aspects qualitatifs
                prompt = prompt.replace("{{scored_leads}}", json.dumps(detailed_scores, ensure_ascii=False))
                
                try:
                    # Appeler GPT-4.1 pour l'analyse qualitative
                    gpt_enrichment = ask_gpt_4_1(prompt)
                    
                    # Vérifier que gpt_enrichment contient "enriched_leads"
                    if not gpt_enrichment or "enriched_leads" not in gpt_enrichment:
                        print(f"[{self.name}] ⚠️ Réponse GPT-4.1 invalide: {gpt_enrichment}")
                        # En mode graceful failure, générer un enrichissement de base
                        gpt_enrichment = {
                            "enriched_leads": [
                                {
                                    "id": lead.get("id", f"lead_{i}"),
                                    "insights": ["Lead automatiquement classifié sans enrichissement GPT"],
                                    "temperature": "warm", # Par défaut, on met warm
                                    "suggested_actions": ["Contacter pour qualification"],
                                    "priority_score": lead.get("global_score", 0.5)
                                }
                                for i, lead in enumerate(detailed_scores)
                            ]
                        }
                except Exception as e:
                    print(f"[{self.name}] ⚠️ Erreur lors de l'appel à GPT-4.1: {str(e)}")
                    # En cas d'erreur, créer une classification de base
                    gpt_enrichment = {
                        "enriched_leads": [
                            {
                                "id": lead.get("id", f"lead_{i}"),
                                "insights": ["Classification de secours suite à une erreur d'API"],
                                "temperature": "warm", # Par défaut, on met warm
                                "suggested_actions": ["Vérifier manuellement ce lead"],
                                "priority_score": lead.get("global_score", 0.5)
                            }
                            for i, lead in enumerate(detailed_scores)
                        ]
                    }
                
                # Fusionner les résultats (règles métier + scoring détaillé + enrichissement GPT)
                final_classification = self._merge_classification_results(detailed_scores, gpt_enrichment)
                
                # Vérifier que la classification finale n'est pas vide
                if not final_classification:
                    print(f"[{self.name}] ⚠️ Classification finale vide, génération d'une classification de secours")
                    # Générer une classification de secours
                    for i, lead in enumerate(detailed_scores):
                        global_score = lead.get("global_score", 0.5)
                        temperature = "cold"
                        if global_score >= 0.85:
                            temperature = "hot"
                        elif global_score >= 0.7:
                            temperature = "warm"
                        
                        lead["classification"] = {
                            "qualite_lead": temperature,
                            "score": global_score,
                            "priorite": "haute" if temperature == "hot" else "moyenne" if temperature == "warm" else "basse"
                        }
                        lead["suggested_actions"] = ["Contacter selon le niveau de priorité"]
                    
                    final_classification = detailed_scores
                
                # Ajouter des informations de classification explicites pour chaque lead
                for lead in final_classification:
                    global_score = lead.get("global_score", 0.5)
                    temp = lead.get("temperature", None)
                    
                    # Si la température n'est pas définie, la déduire du score global
                    if not temp:
                        if global_score >= scoring_config.get("temperature_thresholds", {}).get("hot", 0.85):
                            temp = "hot"
                        elif global_score >= scoring_config.get("temperature_thresholds", {}).get("warm", 0.7):
                            temp = "warm"
                        else:
                            temp = "cold"
                    
                    # Ajouter la classification
                    lead["classification"] = {
                        "qualite_lead": temp.upper(),  # Convertir en majuscules
                        "score": global_score,
                        "priorite": "haute" if temp == "hot" else "moyenne" if temp == "warm" else "basse"
                    }
                
                # Enregistrer les résultats
                result["classified_leads"] = final_classification
                result["metrics"] = {
                    "total_leads": len(final_classification),
                    "avg_global_score": sum(l.get("global_score", 0) for l in final_classification) / len(final_classification) if final_classification else 0,
                    "valid_contacts": len([l for l in final_classification if l.get("email") or l.get("phone")])
                }
                result["status"] = "COMPLETED"
                
            elif operation == "update_from_crm":
                # Mettre à jour le modèle à partir du feedback CRM
                crm_feedback = input_data.get("crm_feedback", [])
                
                if not crm_feedback:
                    result["error"] = "Aucun feedback CRM fourni pour la mise à jour"
                    result["status"] = "FAILED"
                    log_agent(self.name, input_data, result)
                    return result
                
                # Enregistrer le feedback
                update_result = self._update_from_crm_feedback(crm_feedback, scoring_config, learning_cache)
                
                # Enregistrer les résultats
                result.update(update_result)
                result["status"] = "COMPLETED"
                
            elif operation == "adjust_scoring":
                # Ajuster les configurations de scoring
                new_scoring = input_data.get("new_scoring", {})
                
                if not new_scoring:
                    result["error"] = "Aucune nouvelle configuration de scoring fournie"
                    result["status"] = "FAILED"
                    log_agent(self.name, input_data, result)
                    return result
                
                # Mettre à jour la configuration
                adjusted_config = self._adjust_scoring_config(new_scoring, scoring_config)
                
                # Enregistrer les résultats
                result["adjusted_config"] = adjusted_config
                result["status"] = "COMPLETED"
                
            elif operation == "update_heuristics":
                # Mettre à jour les heuristiques métier
                new_heuristics = input_data.get("new_heuristics", {})
                
                if not new_heuristics:
                    result["error"] = "Aucune nouvelle heuristique fournie"
                    result["status"] = "FAILED"
                    log_agent(self.name, input_data, result)
                    return result
                
                # Mettre à jour les heuristiques
                updated_heuristics = self._update_business_heuristics(new_heuristics, business_heuristics)
                
                # Enregistrer les résultats
                result["updated_heuristics"] = updated_heuristics
                result["status"] = "COMPLETED"
                
            elif operation == "analyze_performance":
                # Analyser les performances du modèle
                performance_analysis = self._analyze_classifier_performance(feedback_history, learning_cache)
                
                # Enregistrer les résultats
                result["performance"] = performance_analysis
                result["status"] = "COMPLETED"
                
            else:
                result["error"] = f"Opération non reconnue: {operation}"
                result["status"] = "FAILED"
        
        except Exception as e:
            import traceback
            trace = traceback.format_exc()
            print(f"[{self.name}] 🔴 Exception: {str(e)}\n{trace}")
            result["error"] = f"Erreur lors de l'exécution de l'opération: {str(e)}"
            result["status"] = "FAILED"
        
        # Enregistrer les logs
        log_agent(self.name, input_data, result)
        
        return result
    
    def _load_scoring_config(self):
        """
        Charge la configuration de scoring depuis le fichier
        """
        try:
            with open(self.scoring_config_path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"[{self.name}] ⚠️ Erreur lors du chargement de la configuration de scoring: {str(e)}")
            return {}
    
    def _load_business_heuristics(self):
        """
        Charge les heuristiques métier depuis le fichier
        """
        try:
            with open(self.heuristics_path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"[{self.name}] ⚠️ Erreur lors du chargement des heuristiques métier: {str(e)}")
            return {}
    
    def _load_crm_feedback(self):
        """
        Charge l'historique de feedback CRM depuis le fichier
        """
        try:
            with open(self.feedback_history_path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"[{self.name}] ⚠️ Erreur lors du chargement de l'historique de feedback: {str(e)}")
            return {"feedback_entries": [], "aggregated_stats": {}}
    
    def _load_learning_cache(self):
        """
        Charge le cache d'apprentissage depuis le fichier
        """
        try:
            with open(self.learning_cache_path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"[{self.name}] ⚠️ Erreur lors du chargement du cache d'apprentissage: {str(e)}")
            return {"learned_patterns": {}, "adjustment_factors": {}}
    
    def _prepare_classification_data(self, leads, scoring_config, business_heuristics, learning_cache, extra_context):
        """
        Prépare les données pour la classification
        """
        return {
            "leads": leads,
            "scoring_config": scoring_config,
            "business_heuristics": business_heuristics,
            "learned_patterns": learning_cache.get("learned_patterns", {}),
            "adjustment_factors": learning_cache.get("adjustment_factors", {}),
            "context": extra_context
        }
    
    def _apply_business_heuristics(self, leads, heuristics):
        """
        Applique les heuristiques métier aux leads
        """
        scored_leads = []
        
        for lead in leads:
            # Copier le lead pour ne pas modifier l'original
            scored_lead = lead.copy()
            
            # S'assurer que le lead a un ID
            if "id" not in scored_lead:
                scored_lead["id"] = f"lead_{len(scored_leads)}"
            
            # Initialiser le score basé sur les heuristiques métier
            heuristic_score = 0.5  # Score par défaut
            
            # Vérifier si lead est None avant de l'utiliser
            if lead is None:
                continue
            
            # Appliquer les heuristiques d'industrie
            industry_value = lead.get("industry")
            industry = industry_value.lower() if isinstance(industry_value, str) else ""
            industry_priorities = heuristics.get("industry_priority", {})
            industry_score = industry_priorities.get(industry, industry_priorities.get("default", 0.5))
            
            # Appliquer les heuristiques de poste
            position_value = lead.get("position")
            position = position_value.lower() if isinstance(position_value, str) else ""
            position_match = False
            position_score = 0.5
            
            for position_key, priority in heuristics.get("position_priority", {}).items():
                if position and position_key.lower() in position:
                    position_match = True
                    position_score = priority
                    break
            
            if not position_match:
                position_score = heuristics.get("position_priority", {}).get("default", 0.5)
            
            # Appliquer les heuristiques de taille d'entreprise
            company_size_value = lead.get("company_size")
            company_size = company_size_value.lower() if isinstance(company_size_value, str) else ""
            size_priorities = heuristics.get("company_size_priority", {})
            company_size_score = size_priorities.get(company_size, size_priorities.get("default", 0.5))
            
            # Appliquer les heuristiques de localisation
            location_value = lead.get("location")
            location = location_value.lower() if isinstance(location_value, str) else ""
            location_match = False
            location_score = 0.5
            
            for location_key, priority in heuristics.get("location_priority", {}).items():
                if location_key.lower() in location:
                    location_match = True
                    location_score = priority
                    break
            
            if not location_match:
                location_score = heuristics.get("location_priority", {}).get("default", 0.5)
            
            # Calculer le score heuristique global (moyenne pondérée)
            heuristic_score = (
                industry_score * 0.3 +
                position_score * 0.3 +
                company_size_score * 0.2 +
                location_score * 0.2
            )
            
            # Ajouter le score heuristique au lead
            scored_lead["heuristic_score"] = heuristic_score
            scored_lead["heuristic_details"] = {
                "industry_score": industry_score,
                "position_score": position_score,
                "company_size_score": company_size_score,
                "location_score": location_score
            }
            
            scored_leads.append(scored_lead)
        
        return scored_leads
    
    def _calculate_detailed_scores(self, leads, scoring_config, learning_cache):
        """
        Calcule les scores détaillés pour chaque lead
        """
        detailed_scores = []
        
        for lead in leads:
            detailed_lead = lead.copy()
            
            # S'assurer que le lead a un ID
            if "id" not in detailed_lead:
                detailed_lead["id"] = f"lead_{len(detailed_scores)}"
            
            # 1. Score de qualité d'email
            email = lead.get("email", "")
            # Vérifier si email n'est pas None avant d'appeler _score_email
            email_score = self._score_email(email, scoring_config.get("email", {}), learning_cache) if email is not None else 0.0
            detailed_lead["email_score"] = email_score
            
            # 2. Score de fiabilité de téléphone
            phone = lead.get("phone", "")
            # Vérifier si phone n'est pas None avant d'appeler _score_phone
            phone_score = self._score_phone(phone, scoring_config.get("phone", {}), learning_cache) if phone is not None else 0.0
            detailed_lead["phone_score"] = phone_score
            
            # 3. Score de complétude du profil
            profile_score = self._score_profile(lead, scoring_config.get("profile", {}), learning_cache)
            detailed_lead["profile_score"] = profile_score
            
            # 4. Score global
            global_weights = scoring_config.get("global_weights", {})
            
            global_score = (
                email_score * global_weights.get("email_weight", 0.3) +
                phone_score * global_weights.get("phone_weight", 0.3) +
                profile_score * global_weights.get("profile_weight", 0.4) +
                lead.get("heuristic_score", 0.5) * 0.5  # Ajouter le score heuristique avec un poids de 50%
            ) / 1.5  # Diviser par 1.5 pour normaliser (1 + 0.5)
            
            # Ne pas attribuer de température au lead initialement
            # Stocker uniquement le score global pour référence future

            detailed_lead["global_score"] = global_score
            # Nous ne définissons plus de température ici
            # La température sera définie plus tard par le MessengerAgent après interaction
            detailed_lead["score_details"] = {
                "email": email_score,
                "phone": phone_score,
                "profile": profile_score,
                "heuristic": lead.get("heuristic_score", 0.5)
            }
            
            detailed_scores.append(detailed_lead)
        
        return detailed_scores
    
    def _score_email(self, email, email_config, learning_cache):
        """
        Calcule le score de qualité d'un email
        """
        if not email or not isinstance(email, str):
            return 0.0
        
        # Poids pour différents aspects de l'email
        pattern_weight = email_config.get("pattern_weight", 0.4)
        domain_weight = email_config.get("domain_weight", 0.3)
        length_weight = email_config.get("length_weight", 0.2)
        special_chars_weight = email_config.get("special_chars_weight", 0.1)
        
        # 1. Vérifier le pattern de l'email
        pattern_score = 0.0
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(email_pattern, email):
            pattern_score = 1.0
        
        # 2. Évaluer le domaine
        domain_score = 0.0
        domain = email.split('@')[-1].lower() if '@' in email else ""
        domain_scores = email_config.get("domain_scores", {})
        
        if domain in domain_scores:
            domain_score = domain_scores[domain]
        elif any(domain.endswith('.' + tld) for tld in ['co.uk', 'com.au', 'co.jp', 'fr', 'de', 'it', 'es']):
            domain_score = domain_scores.get("professional_domains", 0.9)
        else:
            domain_score = domain_scores.get("other", 0.4)
        
        # 3. Évaluer la longueur
        length_score = 0.0
        username = email.split('@')[0] if '@' in email else email
        
        if 5 <= len(username) <= 30:
            length_score = 1.0
        elif 3 <= len(username) < 5 or 30 < len(username) <= 40:
            length_score = 0.7
        else:
            length_score = 0.3
        
        # 4. Évaluer les caractères spéciaux
        special_chars_score = 0.0
        special_chars_count = sum(1 for char in username if not char.isalnum())
        
        if special_chars_count == 0:
            special_chars_score = 1.0
        elif special_chars_count <= 2:
            special_chars_score = 0.8
        elif special_chars_count <= 5:
            special_chars_score = 0.5
        else:
            special_chars_score = 0.2
        
        # 5. Ajuster le score avec les patterns appris
        learned_patterns = learning_cache.get("learned_patterns", {}).get("email", {})
        adjustment_factor = learning_cache.get("adjustment_factors", {}).get("email", 1.0)
        
        # Calculer le score final
        raw_score = (
            pattern_score * pattern_weight +
            domain_score * domain_weight +
            length_score * length_weight +
            special_chars_score * special_chars_weight
        )
        
        # Appliquer l'ajustement
        final_score = min(1.0, max(0.0, raw_score * adjustment_factor))
        
        return final_score
    
    def _score_phone(self, phone, phone_config, learning_cache):
        """
        Calcule le score de fiabilité d'un numéro de téléphone
        """
        if not phone or not isinstance(phone, str):
            return 0.0
        
        # Poids pour différents aspects du téléphone
        pattern_weight = phone_config.get("pattern_weight", 0.5)
        length_weight = phone_config.get("length_weight", 0.3)
        prefix_weight = phone_config.get("prefix_weight", 0.2)
        
        # 1. Vérifier le pattern du téléphone
        pattern_score = 0.0
        # Nettoyer le numéro
        cleaned_phone = re.sub(r'[^0-9+]', '', phone)
        
        # Vérifier le format (formats internationaux courants)
        phone_pattern = r'^(\+|00)?[0-9]{1,3}[0-9]{8,12}$'
        if re.match(phone_pattern, cleaned_phone):
            pattern_score = 1.0
        elif re.match(r'^[0-9]{8,12}$', cleaned_phone):
            pattern_score = 0.8  # Format local sans indicatif
        else:
            pattern_score = 0.4
        
        # 2. Évaluer la longueur
        length_score = 0.0
        phone_length = len(cleaned_phone)
        
        if 10 <= phone_length <= 15:
            length_score = 1.0
        elif 8 <= phone_length < 10 or 15 < phone_length <= 17:
            length_score = 0.7
        else:
            length_score = 0.3
        
        # 3. Vérifier le préfixe (code pays)
        prefix_score = 0.0
        country_codes = phone_config.get("country_codes", {})
        
        # Extraire le préfixe potentiel
        prefix = None
        if cleaned_phone.startswith('+'):
            prefix = '+' + cleaned_phone[1:3]  # Prendre les 2 premiers chiffres après le +
        elif cleaned_phone.startswith('00'):
            prefix = cleaned_phone[2:4]  # Prendre les 2 premiers chiffres après 00
        elif cleaned_phone[0] == '0':
            prefix = cleaned_phone[0]  # Format local français commençant par 0
        
        # Vérifier si le préfixe correspond à un pays connu
        prefix_found = False
        for country, codes in country_codes.items():
            if prefix in codes:
                prefix_score = 1.0
                prefix_found = True
                break
        
        if not prefix_found:
            prefix_score = 0.5
        
        # 4. Ajuster le score avec les patterns appris
        learned_patterns = learning_cache.get("learned_patterns", {}).get("phone", {})
        adjustment_factor = learning_cache.get("adjustment_factors", {}).get("phone", 1.0)
        
        # Calculer le score final
        raw_score = (
            pattern_score * pattern_weight +
            length_score * length_weight +
            prefix_score * prefix_weight
        )
        
        # Appliquer l'ajustement
        final_score = min(1.0, max(0.0, raw_score * adjustment_factor))
        
        return final_score
    
    def _score_profile(self, lead, profile_config, learning_cache):
        """
        Calcule le score de complétude et de pertinence d'un profil
        """
        # Poids pour différents aspects du profil
        completeness_weight = profile_config.get("completeness_weight", 0.4)
        relevance_weight = profile_config.get("relevance_weight", 0.6)
        
        # 1. Calculer la complétude du profil
        required_fields = profile_config.get("required_fields", ["name", "email", "phone"])
        optional_fields = profile_config.get("optional_fields", ["company", "position", "industry"])
        
        # Compter les champs requis présents
        required_count = sum(1 for field in required_fields if lead.get(field))
        required_ratio = required_count / len(required_fields) if required_fields else 0
        
        # Compter les champs optionnels présents
        optional_count = sum(1 for field in optional_fields if lead.get(field))
        optional_ratio = optional_count / len(optional_fields) if optional_fields else 0
        
        # Score de complétude (pondéré 70% requis, 30% optionnels)
        completeness_score = required_ratio * 0.7 + optional_ratio * 0.3
        
        # 2. Calculer la pertinence du profil (simulé ici, normalement basé sur d'autres facteurs)
        # Dans une implémentation réelle, cela serait basé sur l'adéquation avec la cible de la campagne
        relevance_score = 0.7  # Valeur par défaut
        
        # Si des données spécifiques sont présentes, ajuster la pertinence
        if lead.get("company_size") and lead.get("industry") and lead.get("position"):
            relevance_score = 0.9
        elif lead.get("company") and lead.get("position"):
            relevance_score = 0.8
        
        # 3. Ajuster le score avec les patterns appris
        adjustment_factor = learning_cache.get("adjustment_factors", {}).get("profile", 1.0)
        
        # Calculer le score final
        raw_score = (
            completeness_score * completeness_weight +
            relevance_score * relevance_weight
        )
        
        # Appliquer l'ajustement
        final_score = min(1.0, max(0.0, raw_score * adjustment_factor))
        
        return final_score
    
    def _merge_classification_results(self, detailed_scores, gpt_enrichment):
        """
        Fusionne les résultats du scoring détaillé avec l'enrichissement GPT
        """
        final_classification = []
        
        # Récupérer l'enrichissement par lead ID
        enriched_leads = {}
        for lead in gpt_enrichment.get("enriched_leads", []):
            lead_id = lead.get("id")
            if lead_id:
                enriched_leads[lead_id] = lead
        
        # Fusionner les résultats
        for scored_lead in detailed_scores:
            lead_id = scored_lead.get("id")
            final_lead = scored_lead.copy()
            
            # Ajouter l'enrichissement GPT si disponible
            if lead_id and lead_id in enriched_leads:
                enrichment = enriched_leads[lead_id]
                
                # Ajouter les insights qualitatifs
                final_lead["qualitative_insights"] = enrichment.get("insights", [])
                
                # Ajuster la température si nécessaire selon l'analyse GPT
                gpt_temperature = enrichment.get("temperature")
                if gpt_temperature:
                    # Si la température calculée et celle de GPT diffèrent,
                    # prendre en compte l'analyse GPT selon un facteur
                    if gpt_temperature != final_lead.get("temperature"):
                        # Garder l'information des deux sources
                        final_lead["calculated_temperature"] = final_lead.get("temperature")
                        final_lead["gpt_temperature"] = gpt_temperature
                        
                        # Prendre la plus chaude des deux si GPT est plus optimiste
                        if (gpt_temperature == "hot" and final_lead.get("temperature") != "hot") or \
                           (gpt_temperature == "warm" and final_lead.get("temperature") == "cold"):
                            final_lead["temperature"] = gpt_temperature
                            final_lead["temperature_note"] = "Ajusté par l'analyse qualitative"
                
                # Ajouter les suggestions d'actions personnalisées
                final_lead["suggested_actions"] = enrichment.get("suggested_actions", [])
                
                # Ajouter le score de priorité
                final_lead["priority_score"] = enrichment.get("priority_score", final_lead.get("global_score", 0))
            
            # Ajouter la classification finale
            final_classification.append(final_lead)
        
        return final_classification
    
    def _update_from_crm_feedback(self, crm_feedback, scoring_config, learning_cache):
        """
        Met à jour le modèle de classification basé sur le feedback du CRM
        """
        results = {
            "updated": True,
            "adjustments_made": [],
            "feedback_processed": len(crm_feedback)
        }
        
        # Charger l'historique de feedback existant
        feedback_history = self._load_crm_feedback()
        
        # Mise à jour des stats agrégées
        current_stats = feedback_history.get("aggregated_stats", {})
        true_positives = current_stats.get("true_positives", 0)
        false_positives = current_stats.get("false_positives", 0)
        true_negatives = current_stats.get("true_negatives", 0)
        false_negatives = current_stats.get("false_negatives", 0)
        
        # Traiter chaque entrée de feedback
        adjustments = []
        for feedback in crm_feedback:
            lead_id = feedback.get("lead_id")
            predicted_temp = feedback.get("predicted_temperature")
            actual_temp = feedback.get("actual_temperature")
            conversion_result = feedback.get("conversion_result", False)
            lead_data = feedback.get("lead_data", {})
            
            # Enregistrer l'entrée dans l'historique
            feedback_entry = {
                "lead_id": lead_id,
                "predicted_temperature": predicted_temp,
                "actual_temperature": actual_temp,
                "conversion_result": conversion_result,
                "timestamp": datetime.datetime.now().isoformat(),
                "lead_data": lead_data
            }
            
            feedback_history["feedback_entries"].append(feedback_entry)
            
            # Mettre à jour les statistiques
            if predicted_temp == "hot" and conversion_result:
                true_positives += 1
            elif predicted_temp == "hot" and not conversion_result:
                false_positives += 1
            elif predicted_temp != "hot" and not conversion_result:
                true_negatives += 1
            elif predicted_temp != "hot" and conversion_result:
                false_negatives += 1
            
            # Analyser le lead pour ajuster les facteurs d'apprentissage
            if predicted_temp != actual_temp:
                adjustment = self._compute_adjustment_factors(
                    lead_data, 
                    predicted_temp, 
                    actual_temp, 
                    learning_cache
                )
                adjustments.append(adjustment)
        
        # Mettre à jour les statistiques agrégées
        total_predictions = true_positives + false_positives + true_negatives + false_negatives
        
        if total_predictions > 0:
            precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
            recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
            f1_score = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
            
            feedback_history["aggregated_stats"] = {
                "true_positives": true_positives,
                "false_positives": false_positives,
                "true_negatives": true_negatives,
                "false_negatives": false_negatives,
                "precision": precision,
                "recall": recall,
                "f1_score": f1_score,
                "last_updated": datetime.datetime.now().isoformat()
            }
        
        # Enregistrer l'historique mis à jour
        with open(self.feedback_history_path, "w") as f:
            json.dump(feedback_history, f, indent=2)
        
        # Appliquer les ajustements au cache d'apprentissage
        learning_cache = self._apply_adjustments(adjustments, learning_cache)
        
        # Enregistrer le cache d'apprentissage mis à jour
        with open(self.learning_cache_path, "w") as f:
            json.dump(learning_cache, f, indent=2)
        
        # Ajouter les résultats
        results["current_performance"] = feedback_history["aggregated_stats"]
        results["learning_updates"] = adjustments
        
        return results
    
    def _compute_adjustment_factors(self, lead_data, predicted_temp, actual_temp, learning_cache):
        """
        Calcule les facteurs d'ajustement basés sur la différence entre la température prédite et réelle
        """
        # Initialiser les facteurs d'ajustement
        adjustments = {
            "email": 1.0,
            "phone": 1.0,
            "profile": 1.0
        }
        
        # Déterminer la direction de l'ajustement
        # Si la prédiction était trop froide (sous-estimée), augmenter les facteurs
        # Si la prédiction était trop chaude (surestimée), diminuer les facteurs
        adjustment_direction = 1.0
        if (predicted_temp == "cold" and actual_temp == "warm") or \
           (predicted_temp == "warm" and actual_temp == "hot") or \
           (predicted_temp == "cold" and actual_temp == "hot"):
            adjustment_direction = 1.05  # Augmenter de 5%
        elif (predicted_temp == "hot" and actual_temp == "warm") or \
             (predicted_temp == "warm" and actual_temp == "cold") or \
             (predicted_temp == "hot" and actual_temp == "cold"):
            adjustment_direction = 0.95  # Diminuer de 5%
        
        # Analyser quels éléments ont pu causer l'erreur
        if lead_data.get("email") and "@" in lead_data.get("email", ""):
            email_domain = lead_data["email"].split('@')[-1].lower()
            learned_patterns = learning_cache.get("learned_patterns", {})
            
            # Enregistrer le pattern de domaine
            if "email" not in learned_patterns:
                learned_patterns["email"] = {}
            
            if email_domain not in learned_patterns["email"]:
                learned_patterns["email"][email_domain] = {
                    "occurrences": 0,
                    "correct_predictions": 0
                }
            
            learned_patterns["email"][email_domain]["occurrences"] += 1
            if predicted_temp == actual_temp:
                learned_patterns["email"][email_domain]["correct_predictions"] += 1
            
            # Calculer l'ajustement pour l'email
            adjustments["email"] = adjustment_direction
        
        # Faire de même pour le téléphone et le profil
        if lead_data.get("phone"):
            # Pattern téléphone: préfixe (2 premiers chiffres)
            phone_prefix = re.sub(r'[^0-9+]', '', lead_data["phone"])[:2]
            
            if "phone" not in learning_cache.get("learned_patterns", {}):
                learning_cache["learned_patterns"]["phone"] = {}
            
            if phone_prefix not in learning_cache["learned_patterns"]["phone"]:
                learning_cache["learned_patterns"]["phone"][phone_prefix] = {
                    "occurrences": 0,
                    "correct_predictions": 0
                }
            
            learning_cache["learned_patterns"]["phone"][phone_prefix]["occurrences"] += 1
            if predicted_temp == actual_temp:
                learning_cache["learned_patterns"]["phone"][phone_prefix]["correct_predictions"] += 1
            
            # Calculer l'ajustement pour le téléphone
            adjustments["phone"] = adjustment_direction
        
        # Profil: industrie, poste, etc.
        if lead_data.get("industry") or lead_data.get("position"):
            profile_key = (lead_data.get("industry", "") + "_" + lead_data.get("position", "")).lower()
            
            if "profile" not in learning_cache.get("learned_patterns", {}):
                learning_cache["learned_patterns"]["profile"] = {}
            
            if profile_key not in learning_cache["learned_patterns"]["profile"]:
                learning_cache["learned_patterns"]["profile"][profile_key] = {
                    "occurrences": 0,
                    "correct_predictions": 0
                }
            
            learning_cache["learned_patterns"]["profile"][profile_key]["occurrences"] += 1
            if predicted_temp == actual_temp:
                learning_cache["learned_patterns"]["profile"][profile_key]["correct_predictions"] += 1
            
            # Calculer l'ajustement pour le profil
            adjustments["profile"] = adjustment_direction
        
        return {
            "lead_id": lead_data.get("id"),
            "predicted_temperature": predicted_temp,
            "actual_temperature": actual_temp,
            "adjustments": adjustments,
            "timestamp": datetime.datetime.now().isoformat()
        }
    
    def _apply_adjustments(self, adjustments, learning_cache):
        """
        Applique les ajustements calculés au cache d'apprentissage
        """
        current_factors = learning_cache.get("adjustment_factors", {
            "email": 1.0,
            "phone": 1.0,
            "profile": 1.0
        })
        
        # Calculer les nouveaux facteurs (moyenne pondérée)
        email_adjustments = [adj["adjustments"]["email"] for adj in adjustments if "email" in adj["adjustments"]]
        phone_adjustments = [adj["adjustments"]["phone"] for adj in adjustments if "phone" in adj["adjustments"]]
        profile_adjustments = [adj["adjustments"]["profile"] for adj in adjustments if "profile" in adj["adjustments"]]
        
        # Appliquer les ajustements (avec un facteur de lissage pour éviter les changements brusques)
        smoothing_factor = 0.7  # 70% ancienne valeur, 30% nouvelle valeur
        
        if email_adjustments:
            avg_email_adjustment = sum(email_adjustments) / len(email_adjustments)
            current_factors["email"] = current_factors.get("email", 1.0) * smoothing_factor + avg_email_adjustment * (1 - smoothing_factor)
        
        if phone_adjustments:
            avg_phone_adjustment = sum(phone_adjustments) / len(phone_adjustments)
            current_factors["phone"] = current_factors.get("phone", 1.0) * smoothing_factor + avg_phone_adjustment * (1 - smoothing_factor)
        
        if profile_adjustments:
            avg_profile_adjustment = sum(profile_adjustments) / len(profile_adjustments)
            current_factors["profile"] = current_factors.get("profile", 1.0) * smoothing_factor + avg_profile_adjustment * (1 - smoothing_factor)
        
        # Mettre à jour les facteurs d'ajustement
        learning_cache["adjustment_factors"] = current_factors
        learning_cache["last_learning_update"] = datetime.datetime.now().isoformat()
        
        # Stocker les ajustements dans l'historique d'apprentissage
        if len(adjustments) > 0:
            if "successful_classifications" not in learning_cache:
                learning_cache["successful_classifications"] = []
            if "misclassifications" not in learning_cache:
                learning_cache["misclassifications"] = []
            
            for adjustment in adjustments:
                if adjustment["predicted_temperature"] == adjustment["actual_temperature"]:
                    learning_cache["successful_classifications"].append(adjustment)
                else:
                    learning_cache["misclassifications"].append(adjustment)
        
        return learning_cache
    
    def _adjust_scoring_config(self, new_scoring, current_config):
        """
        Ajuste la configuration de scoring selon les paramètres fournis
        """
        # Copier la configuration actuelle
        updated_config = current_config.copy()
        
        # Mettre à jour les poids globaux si spécifiés
        if "global_weights" in new_scoring:
            updated_config["global_weights"] = new_scoring["global_weights"]
        
        # Mettre à jour les seuils de température si spécifiés
        if "temperature_thresholds" in new_scoring:
            updated_config["temperature_thresholds"] = new_scoring["temperature_thresholds"]
        
        # Mettre à jour les configurations spécifiques
        for key in ["email", "phone", "profile"]:
            if key in new_scoring:
                if key not in updated_config:
                    updated_config[key] = {}
                
                # Mettre à jour les poids
                if f"{key}_weights" in new_scoring:
                    for weight_key, weight_value in new_scoring[f"{key}_weights"].items():
                        updated_config[key][weight_key] = weight_value
                
                # Mettre à jour les autres paramètres spécifiques
                for param_key, param_value in new_scoring[key].items():
                    updated_config[key][param_key] = param_value
        
        # Enregistrer la date de mise à jour
        updated_config["last_updated"] = datetime.datetime.now().isoformat()
        
        # Enregistrer la configuration mise à jour
        with open(self.scoring_config_path, "w") as f:
            json.dump(updated_config, f, indent=2)
        
        return updated_config
    
    def _update_business_heuristics(self, new_heuristics, current_heuristics):
        """
        Met à jour les heuristiques métier selon les paramètres fournis
        """
        # Copier les heuristiques actuelles
        updated_heuristics = current_heuristics.copy()
        
        # Mettre à jour les heuristiques par catégorie
        for category in ["industry_priority", "position_priority", "company_size_priority", "location_priority"]:
            if category in new_heuristics:
                if category not in updated_heuristics:
                    updated_heuristics[category] = {}
                
                # Mettre à jour ou ajouter des valeurs
                for key, value in new_heuristics[category].items():
                    updated_heuristics[category][key] = value
        
        # Enregistrer la date de mise à jour
        updated_heuristics["last_updated"] = datetime.datetime.now().isoformat()
        
        # Enregistrer les heuristiques mises à jour
        with open(self.heuristics_path, "w") as f:
            json.dump(updated_heuristics, f, indent=2)
        
        return updated_heuristics
    
    def _analyze_classifier_performance(self, feedback_history, learning_cache):
        """
        Analyse les performances du classifier sur la base des feedbacks du CRM
        """
        # Extraire les statistiques agrégées
        stats = feedback_history.get("aggregated_stats", {})
        
        # Créer l'analyse de performance
        performance = {
            "accuracy": {
                "overall": 0,
                "by_temperature": {
                    "hot": 0,
                    "warm": 0,
                    "cold": 0
                }
            },
            "precision": stats.get("precision", 0),
            "recall": stats.get("recall", 0),
            "f1_score": stats.get("f1_score", 0),
            "confusion_matrix": {
                "true_positives": stats.get("true_positives", 0),
                "false_positives": stats.get("false_positives", 0),
                "true_negatives": stats.get("true_negatives", 0),
                "false_negatives": stats.get("false_negatives", 0)
            },
            "feedback_count": len(feedback_history.get("feedback_entries", [])),
            "last_update": stats.get("last_updated", datetime.datetime.now().isoformat())
        }
        
        # Calculer la précision globale
        total = sum(performance["confusion_matrix"].values())
        if total > 0:
            correct = performance["confusion_matrix"]["true_positives"] + performance["confusion_matrix"]["true_negatives"]
            performance["accuracy"]["overall"] = correct / total
        
        # Calculer la précision par température
        feedback_entries = feedback_history.get("feedback_entries", [])
        temp_counts = {"hot": 0, "warm": 0, "cold": 0}
        temp_correct = {"hot": 0, "warm": 0, "cold": 0}
        
        for entry in feedback_entries:
            predicted = entry.get("predicted_temperature")
            actual = entry.get("actual_temperature")
            
            if predicted:
                temp_counts[predicted] = temp_counts.get(predicted, 0) + 1
                if predicted == actual:
                    temp_correct[predicted] = temp_correct.get(predicted, 0) + 1
        
        for temp in ["hot", "warm", "cold"]:
            if temp_counts.get(temp, 0) > 0:
                performance["accuracy"]["by_temperature"][temp] = temp_correct.get(temp, 0) / temp_counts.get(temp, 1)
        
        # Analyser les patterns d'apprentissage
        pattern_performance = {
            "email": {},
            "phone": {},
            "profile": {}
        }
        
        learned_patterns = learning_cache.get("learned_patterns", {})
        
        for category in ["email", "phone", "profile"]:
            category_patterns = learned_patterns.get(category, {})
            for pattern, data in category_patterns.items():
                occurrences = data.get("occurrences", 0)
                if occurrences > 0:
                    correct_rate = data.get("correct_predictions", 0) / occurrences
                    pattern_performance[category][pattern] = {
                        "occurrences": occurrences,
                        "correct_rate": correct_rate
                    }
        
        performance["pattern_performance"] = pattern_performance
        performance["adjustment_factors"] = learning_cache.get("adjustment_factors", {})
        
        # Identifier les domaines à améliorer
        areas_to_improve = []
        
        # Si la précision est faible pour certaines températures
        for temp, accuracy in performance["accuracy"]["by_temperature"].items():
            if accuracy < 0.7:  # Seuil arbitraire de 70%
                areas_to_improve.append(f"Précision pour la température {temp}: {accuracy*100:.1f}%")
        
        # Si certains patterns ont une faible performance
        for category, patterns in pattern_performance.items():
            for pattern, data in patterns.items():
                if data["occurrences"] >= 5 and data["correct_rate"] < 0.6:  # Au moins 5 occurrences et moins de 60% correct
                    areas_to_improve.append(f"Pattern {category} '{pattern}': {data['correct_rate']*100:.1f}% de précision sur {data['occurrences']} occurrences")
        
        performance["areas_to_improve"] = areas_to_improve
        
        # Recommandations d'ajustement
        recommendations = []
        
        if performance["precision"] < 0.7:
            recommendations.append("Augmenter les seuils de température pour réduire les faux positifs")
        
        if performance["recall"] < 0.7:
            recommendations.append("Diminuer les seuils de température pour réduire les faux négatifs")
        
        # Recommandations basées sur les facteurs d'ajustement
        adjustment_factors = learning_cache.get("adjustment_factors", {})
        for category, factor in adjustment_factors.items():
            if factor < 0.85:
                recommendations.append(f"Le score {category} est potentiellement surestimé (facteur d'ajustement: {factor:.2f})")
            elif factor > 1.15:
                recommendations.append(f"Le score {category} est potentiellement sous-estimé (facteur d'ajustement: {factor:.2f})")
        
        performance["recommendations"] = recommendations
        
        return performance
