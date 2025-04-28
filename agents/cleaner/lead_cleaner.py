from agents.base.base import AgentBase
from utils.llm import ask_gpt_4_1
from logs.agent_logger import log_agent
import re
import json
import datetime
import os

class CleanerAgent(AgentBase):
    def __init__(self):
        super().__init__("CleanerAgent")
        self.prompt_path = "prompts/cleaner_agent_prompt.txt"
        self.error_patterns_file = "logs/cleaning_patterns.json"
        self._ensure_error_patterns_file_exists()
        
    def _ensure_error_patterns_file_exists(self):
        """Ensures that the error patterns file exists"""
        if not os.path.exists(self.error_patterns_file):
            with open(self.error_patterns_file, "w") as f:
                json.dump({
                    "email_patterns": [],
                    "phone_patterns": [],
                    "name_patterns": [],
                    "address_patterns": [],
                    "anomalies": [],
                    "last_updated": datetime.datetime.now().isoformat()
                }, f, indent=2)

    def run(self, input_data: dict) -> dict:
        print(f"[{self.name}] 🧹 Nettoyage et validation des leads...")
        
        # Récupérer les données à nettoyer
        leads = input_data.get("data", [])
        validation_level = input_data.get("validation_level", "standard")  # basic, standard, enhanced
        niche = input_data.get("niche", "")  # Contexte de la niche pour validations spécifiques
        
        if not leads:
            result = {
                "error": "Aucune donnée à nettoyer", 
                "clean_data": [],
                "status": "FAILED",
                "message": "Un ensemble de leads valide est requis pour le nettoyage. L'agent StrategyAgent ou ScraperAgent doit fournir des données."
            }
            log_agent(self.name, input_data, result)
            return result
        
        # Charger les patterns d'erreurs connus
        error_patterns = self._load_error_patterns()
        
        # Appliquer le nettoyage de base (validation technique)
        cleaned_leads = []
        anomalies = []
        
        for lead in leads:
            # Initialiser les flags de validation
            lead_valid = True
            validation_errors = []
            has_valid_contact = False  # Nouveau flag pour vérifier si au moins un canal de contact est valide

            # Copier le lead original pour le nettoyer
            clean_lead = lead.copy()

            # 1. Nettoyer et valider l'email
            email_valid = False
            if "email" in clean_lead:
                email_result = self._validate_email(clean_lead["email"], error_patterns["email_patterns"])
                if email_result["valid"]:
                    has_valid_contact = True  # Email valide, donc un canal de contact est disponible
                    email_valid = True
                else:
                    validation_errors.append(f"Email invalide: {email_result['reason']}")
                clean_lead["email"] = email_result["cleaned_value"]

            # 2. Nettoyer et valider le téléphone
            phone_valid = False
            if "phone" in clean_lead:
                phone_result = self._validate_phone(clean_lead["phone"], error_patterns["phone_patterns"], niche)
                if phone_result["valid"]:
                    has_valid_contact = True  # Téléphone valide, donc un canal de contact est disponible
                    phone_valid = True
                else:
                    validation_errors.append(f"Téléphone invalide: {phone_result['reason']}")
                clean_lead["phone"] = phone_result["cleaned_value"]
                
            # Un lead n'est invalide que si AUCUN canal de contact n'est disponible
            if not has_valid_contact:
                lead_valid = False
                # Ajouter un message d'erreur clair si aucun canal n'est valide
                if not email_valid and not phone_valid:
                    validation_errors.append("Aucun canal de contact valide (email ET téléphone manquants ou invalides)")
            
            # 3. Nettoyer et valider le nom/entreprise
            if "name" in clean_lead:
                name_result = self._validate_name(clean_lead["name"], error_patterns["name_patterns"])
                if not name_result["valid"]:
                    lead_valid = False
                    validation_errors.append(f"Nom invalide: {name_result['reason']}")
                clean_lead["name"] = name_result["cleaned_value"]
            
            # 4. Nettoyer et valider l'adresse
            if "address" in clean_lead:
                address_result = self._validate_address(clean_lead["address"], error_patterns["address_patterns"], niche)
                if not address_result["valid"]:
                    lead_valid = False
                    validation_errors.append(f"Adresse invalide: {address_result['reason']}")
                clean_lead["address"] = address_result["cleaned_value"]
            
            # Si validation améliorée, vérifier la cohérence des données
            if validation_level in ["enhanced", "advanced"] and lead_valid:
                coherence_result = self._check_data_coherence(clean_lead, niche)
                if not coherence_result["coherent"]:
                    anomalies.append({
                        "lead_id": clean_lead.get("id", "unknown"),
                        "type": "coherence",
                        "description": coherence_result["description"],
                        "original_data": lead,
                        "cleaned_data": clean_lead
                    })
                    # Pour la validation avancée, on considère les anomalies comme bloquantes
                    if validation_level == "advanced":
                        lead_valid = False
                        validation_errors.append(f"Anomalie: {coherence_result['description']}")
            
            # Ajouter les métadonnées de validation
            clean_lead["validation"] = {
                "valid": lead_valid,
                "errors": validation_errors,
                "level": validation_level,
                "cleaned_at": datetime.datetime.now().isoformat()
            }
            
            # Si le lead est valide ou si on accepte les leads partiellement valides
            if lead_valid or validation_level != "advanced":
                cleaned_leads.append(clean_lead)
        
        # Si des anomalies sont détectées, utiliser l'IA pour les interpréter
        if anomalies and validation_level in ["enhanced", "advanced"]:
            anomaly_analysis = self._analyze_anomalies(anomalies, niche)
            # Mettre à jour les patterns d'erreurs avec les nouveaux patterns détectés
            self._update_error_patterns(anomaly_analysis.get("new_patterns", []))
        else:
            anomaly_analysis = {"summary": "Aucune anomalie détectée", "new_patterns": []}
        
        # Préparer le résultat
        result = {
            "clean_data": cleaned_leads,
            "validation_stats": {
                "total": len(leads),
                "valid": sum(1 for lead in cleaned_leads if lead["validation"]["valid"]),
                "invalid": sum(1 for lead in cleaned_leads if not lead["validation"]["valid"]),
                "anomalies_count": len(anomalies)
            },
            "anomaly_analysis": anomaly_analysis,
            "validation_level": validation_level
        }
        
        # Enregistrer les logs
        log_agent(self.name, input_data, result)
        
        return result
    
    def _validate_email(self, email, known_patterns):
        """Valide et nettoie une adresse email"""
        if not email:
            return {"valid": False, "cleaned_value": "", "reason": "Email vide"}
        
        # Nettoyer les espaces et caractères indésirables
        cleaned_email = email.strip().lower()
        
        # Expression régulière pour vérifier le format de base d'un email
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_regex, cleaned_email):
            return {"valid": False, "cleaned_value": cleaned_email, "reason": "Format invalide"}
        
        # Vérifier les patterns d'erreurs connus
        for pattern in known_patterns:
            if re.search(pattern["regex"], cleaned_email):
                return {"valid": False, "cleaned_value": cleaned_email, "reason": pattern["description"]}
        
        # Vérification avancée : domaine existant (simulation)
        domain = cleaned_email.split('@')[1]
        common_typos = {"gmial.com": "gmail.com", "hotmial.com": "hotmail.com", "yahooo.com": "yahoo.com"}
        
        if domain in common_typos:
            corrected_email = cleaned_email.replace(domain, common_typos[domain])
            return {
                "valid": True, 
                "cleaned_value": corrected_email, 
                "reason": f"Domaine corrigé: {domain} -> {common_typos[domain]}"
            }
        
        return {"valid": True, "cleaned_value": cleaned_email, "reason": ""}
    
    def _validate_phone(self, phone, known_patterns, niche):
        """Valide et nettoie un numéro de téléphone"""
        if not phone:
            return {"valid": False, "cleaned_value": "", "reason": "Téléphone vide"}
        
        # Nettoyer les caractères non numériques
        cleaned_phone = re.sub(r'[^\d+]', '', phone)
        
        # Vérifier la longueur minimale (après nettoyage)
        if len(cleaned_phone) < 8:
            return {"valid": False, "cleaned_value": cleaned_phone, "reason": "Numéro trop court"}
        
        # Vérifier les patterns d'erreurs connus
        for pattern in known_patterns:
            if re.search(pattern["regex"], cleaned_phone):
                return {"valid": False, "cleaned_value": cleaned_phone, "reason": pattern["description"]}
        
        # Vérification spécifique au contexte (exemple: vérification de l'indicatif pays pour une niche)
        if "france" in niche.lower() and not (cleaned_phone.startswith('+33') or cleaned_phone.startswith('0')):
            return {
                "valid": False, 
                "cleaned_value": cleaned_phone, 
                "reason": "Indicatif pays incorrect pour la France"
            }
        
        # Normalisation du format (exemple)
        if cleaned_phone.startswith('0') and len(cleaned_phone) == 10:  # Format français
            normalized_phone = "+33" + cleaned_phone[1:]
            return {"valid": True, "cleaned_value": normalized_phone, "reason": ""}
        
        return {"valid": True, "cleaned_value": cleaned_phone, "reason": ""}
    
    def _validate_name(self, name, known_patterns):
        """Valide et nettoie un nom (personne ou entreprise)"""
        if not name:
            return {"valid": False, "cleaned_value": "", "reason": "Nom vide"}
        
        # Nettoyer les espaces excessifs
        cleaned_name = re.sub(r'\s+', ' ', name).strip()
        
        # Vérifier la longueur minimale
        if len(cleaned_name) < 2:
            return {"valid": False, "cleaned_value": cleaned_name, "reason": "Nom trop court"}
        
        # Vérifier les patterns d'erreurs connus
        for pattern in known_patterns:
            if re.search(pattern["regex"], cleaned_name, re.IGNORECASE):
                return {"valid": False, "cleaned_value": cleaned_name, "reason": pattern["description"]}
        
        # Correction de la casse (première lettre de chaque mot en majuscule)
        corrected_name = ' '.join(word.capitalize() for word in cleaned_name.split())
        
        return {"valid": True, "cleaned_value": corrected_name, "reason": ""}
    
    def _validate_address(self, address, known_patterns, niche):
        """Valide et nettoie une adresse"""
        if not address:
            return {"valid": False, "cleaned_value": "", "reason": "Adresse vide"}
        
        # Nettoyer les espaces excessifs
        cleaned_address = re.sub(r'\s+', ' ', address).strip()
        
        # Vérifier la longueur minimale
        if len(cleaned_address) < 8:
            return {"valid": False, "cleaned_value": cleaned_address, "reason": "Adresse trop courte"}
        
        # Vérifier les patterns d'erreurs connus
        for pattern in known_patterns:
            if re.search(pattern["regex"], cleaned_address, re.IGNORECASE):
                return {"valid": False, "cleaned_value": cleaned_address, "reason": pattern["description"]}
        
        # Vérification spécifique au contexte (exemple)
        if "france" in niche.lower() and not re.search(r'\b\d{5}\b', cleaned_address):
            return {
                "valid": False, 
                "cleaned_value": cleaned_address, 
                "reason": "Code postal français manquant"
            }
        
        return {"valid": True, "cleaned_value": cleaned_address, "reason": ""}
    
    def _check_data_coherence(self, lead, niche):
        """Vérifie la cohérence globale des données du lead par rapport au contexte"""
        # Initialiser le résultat
        result = {"coherent": True, "description": ""}
        
        # Exemples de vérifications de cohérence:
        
        # 1. Vérifier la cohérence entre email et nom d'entreprise
        if "email" in lead and "name" in lead:
            email_domain = lead["email"].split('@')[1]
            # Si l'email est une adresse professionnelle, le domaine devrait avoir un lien avec le nom
            if not email_domain.startswith(('gmail', 'yahoo', 'hotmail', 'outlook', 'aol', 'free', 'orange')):
                # Comparer domaine et nom (simplification extrême pour l'exemple)
                name_parts = [part.lower() for part in lead["name"].split()]
                domain_parts = [part.lower() for part in email_domain.split('.')[0].split('-')]
                
                if not any(part in domain_parts for part in name_parts if len(part) > 3):
                    result["coherent"] = False
                    result["description"] = f"Le domaine de l'email ({email_domain}) ne semble pas correspondre au nom ({lead['name']})"
        
        # 2. Vérifier la cohérence du téléphone avec la région (exemple)
        if "phone" in lead and "france" in niche.lower():
            if not (lead["phone"].startswith('+33') or lead["phone"].startswith('0')):
                result["coherent"] = False
                result["description"] = f"Numéro non français ({lead['phone']}) pour une campagne française"
        
        # 3. Vérifier la présence improbable de données dans un champ
        if "notes" in lead and lead["notes"]:
            # Détecter des motifs qui ressemblent à des emails ou téléphones dans les notes
            email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            phone_pattern = r'\b\d{2}[\s.-]?\d{2}[\s.-]?\d{2}[\s.-]?\d{2}[\s.-]?\d{2}\b'
            
            if re.search(email_pattern, lead["notes"]) or re.search(phone_pattern, lead["notes"]):
                result["coherent"] = False
                result["description"] = "Contact potentiel détecté dans les notes plutôt que dans les champs dédiés"
        
        return result
    
    def _analyze_anomalies(self, anomalies, niche):
        """Utilise l'IA pour analyser les anomalies détectées"""
        # Préparer le prompt pour l'IA
        anomaly_examples = []
        for i, anomaly in enumerate(anomalies[:5]):  # Limiter à 5 exemples pour le prompt
            anomaly_examples.append({
                "type": anomaly["type"],
                "description": anomaly["description"],
                "original_data": anomaly["original_data"],
                "cleaned_data": anomaly["cleaned_data"]
            })
        
        prompt = f"""
        En tant qu'expert en nettoyage de données, analyse ces anomalies détectées lors du nettoyage de leads pour la niche: {niche}.

        Anomalies:
        {json.dumps(anomaly_examples, indent=2)}
        
        Tâches:
        1. Fais une synthèse des types d'anomalies détectées
        2. Suggère des explications possibles pour ces anomalies
        3. Propose des nouveaux patterns de validation à ajouter au système
        4. Recommande des améliorations pour le processus de nettoyage
        
        Format de réponse attendu:
        - summary: <résumé des anomalies>
        - explanations: <liste d'explications possibles>
        - new_patterns: <liste de nouveaux patterns de validation>
           - chaque pattern contient: field (email/phone/name/address), regex, description
        - recommendations: <liste de recommandations pour améliorer le nettoyage>
        """
        
        # Appeler l'IA pour l'analyse
        analysis = ask_gpt_4_1(prompt)
        
        return analysis
    
    def _load_error_patterns(self):
        """Charge les patterns d'erreurs connus depuis le fichier de stockage"""
        try:
            with open(self.error_patterns_file, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"[{self.name}] ⚠️ Erreur lors du chargement des patterns: {str(e)}")
            # Retourner une structure par défaut en cas d'erreur
            return {
                "email_patterns": [],
                "phone_patterns": [],
                "name_patterns": [],
                "address_patterns": [],
                "anomalies": []
            }
    
    def _update_error_patterns(self, new_patterns):
        """Met à jour le fichier des patterns d'erreurs avec de nouveaux patterns détectés"""
        try:
            # Charger les patterns existants
            current_patterns = self._load_error_patterns()
            
            # Ajouter les nouveaux patterns dans les catégories appropriées
            for pattern in new_patterns:
                field = pattern.get("field", "").lower()
                if field in ["email", "phone", "name", "address"]:
                    pattern_category = f"{field}_patterns"
                    
                    # Vérifier si le pattern existe déjà (éviter les doublons)
                    pattern_exists = any(
                        existing.get("regex") == pattern.get("regex") 
                        for existing in current_patterns.get(pattern_category, [])
                    )
                    
                    if not pattern_exists and "regex" in pattern and "description" in pattern:
                        if pattern_category not in current_patterns:
                            current_patterns[pattern_category] = []
                        
                        # Ajouter le pattern avec timestamp
                        pattern["added_at"] = datetime.datetime.now().isoformat()
                        current_patterns[pattern_category].append(pattern)
            
            # Mettre à jour le timestamp
            current_patterns["last_updated"] = datetime.datetime.now().isoformat()
            
            # Sauvegarder les patterns mis à jour
            with open(self.error_patterns_file, "w") as f:
                json.dump(current_patterns, f, indent=2)
            
            print(f"[{self.name}] ✅ Patterns de nettoyage mis à jour")
            return True
        
        except Exception as e:
            print(f"[{self.name}] ⚠️ Erreur lors de la mise à jour des patterns: {str(e)}")
            return False
