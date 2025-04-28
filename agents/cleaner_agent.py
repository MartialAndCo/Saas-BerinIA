from datetime import datetime
import time
import json
import re
from typing import Dict, Any, List, Optional
import logging
import pandas as pd

from .base import BaseAgent
from .utils.llm import ask_llm, generate_structured_response

class CleanerAgent(BaseAgent):
    """
    Agent responsable du nettoyage et de la normalisation des données.
    
    Cet agent nettoie et normalise les données de leads, supprime les doublons,
    corrige les erreurs et standardise les formats.
    """
    
    def __init__(self, agent_id, db_session):
        super().__init__(agent_id, db_session)
    
    def run(self, input_data):
        """
        Exécute l'agent de nettoyage.
        
        Args:
            input_data (dict): Les données d'entrée, qui peuvent inclure:
                - leads: Liste des leads à nettoyer
                - campaign_id: ID de la campagne associée
                - rules: Règles de nettoyage spécifiques
                - source: Source des leads
                
        Returns:
            dict: Résultats du nettoyage
        """
        self.logger.info(f"Lancement de CleanerAgent avec {len(input_data.get('leads', []))} leads")
        
        start_time = time.time()
        
        try:
            # Extraire les paramètres
            leads = input_data.get('leads', [])
            campaign_id = input_data.get('campaign_id')
            rules = input_data.get('rules', {})
            source = input_data.get('source', 'unknown')
            
            if not leads:
                return {
                    'status': 'error',
                    'message': 'Aucun lead à nettoyer',
                    'cleaned_leads': []
                }
            
            # Convertir les leads en DataFrame pour faciliter le traitement
            leads_df = pd.DataFrame(leads)
            
            # Conserver une copie du nombre original
            original_count = len(leads_df)
            
            # Processus de nettoyage en plusieurs étapes
            # 1. Normalisation des champs
            normalized_df = self._normalize_fields(leads_df, rules)
            
            # 2. Nettoyage des données
            cleaned_df = self._clean_data(normalized_df, rules)
            
            # 3. Déduplication
            deduplicated_df = self._deduplicate(cleaned_df, rules)
            
            # 4. Validation finale
            validated_df, invalid_df = self._validate_leads(deduplicated_df, rules)
            
            # Convertir les résultats en liste de dictionnaires
            cleaned_leads = validated_df.to_dict(orient='records')
            invalid_leads = invalid_df.to_dict(orient='records')
            
            # Statistiques de nettoyage
            cleaning_stats = {
                'original_count': original_count,
                'cleaned_count': len(cleaned_leads),
                'invalid_count': len(invalid_leads),
                'duplicates_removed': original_count - len(deduplicated_df),
                'fields_normalized': self._count_normalized_fields(leads_df, normalized_df),
                'cleaning_rules_applied': len(rules)
            }
            
            execution_time = time.time() - start_time
            
            # Enregistrer les leads nettoyés dans la base de données si un campaign_id est fourni
            if campaign_id and cleaned_leads:
                self._save_cleaned_leads(cleaned_leads, campaign_id, source)
            
            # Préparer les résultats
            results = {
                'status': 'success',
                'message': f"Nettoyage terminé: {len(cleaned_leads)} leads valides, {len(invalid_leads)} invalides",
                'cleaned_leads': cleaned_leads,
                'invalid_leads': invalid_leads,
                'stats': cleaning_stats,
                'execution_time': execution_time
            }
            
            # Logging des résultats
            self.log_execution(
                operation="clean_leads",
                input_data={'lead_count': original_count, 'campaign_id': campaign_id, 'source': source},
                output_data=results,
                status="success",
                execution_time=execution_time
            )
            
            return results
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Erreur lors de l'exécution de CleanerAgent: {str(e)}")
            
            # Logging de l'erreur
            self.log_execution(
                operation="clean_leads",
                input_data=input_data,
                output_data={"error": str(e)},
                status="error",
                execution_time=execution_time
            )
            
            return {
                'status': 'error',
                'message': str(e),
                'cleaned_leads': []
            }
    
    def _normalize_fields(self, leads_df, rules):
        """
        Normalise les noms et formats des champs.
        
        Args:
            leads_df: DataFrame des leads
            rules: Règles de nettoyage
            
        Returns:
            DataFrame: DataFrame avec champs normalisés
        """
        # Copie pour éviter de modifier l'original
        df = leads_df.copy()
        
        # Normalisation des noms de colonnes
        column_mapping = {
            'first_name': ['firstname', 'first', 'prenom', 'prénom', 'given_name'],
            'last_name': ['lastname', 'last', 'nom', 'family_name', 'surname'],
            'email': ['mail', 'email_address', 'courriel', 'emailaddress'],
            'phone': ['telephone', 'phone_number', 'mobile', 'tel', 'phonenumber', 'tel_number'],
            'company': ['organisation', 'organization', 'enterprise', 'entreprise', 'employer'],
            'job_title': ['title', 'position', 'role', 'job', 'poste', 'fonction'],
            'country': ['pays', 'nation', 'location_country'],
            'city': ['ville', 'town', 'location_city'],
            'industry': ['sector', 'secteur', 'domaine', 'domain', 'field'],
            'website': ['site', 'site_web', 'web', 'url', 'site_internet']
        }
        
        # Appliquer le mapping de colonnes
        for target_col, source_cols in column_mapping.items():
            for source_col in source_cols:
                if source_col in df.columns and target_col not in df.columns:
                    df[target_col] = df[source_col]
                    df = df.drop(columns=[source_col])
                elif source_col in df.columns and target_col in df.columns:
                    # Si les deux colonnes existent, utiliser celle qui n'est pas vide
                    mask = df[target_col].isna() | (df[target_col] == '')
                    df.loc[mask, target_col] = df.loc[mask, source_col]
                    df = df.drop(columns=[source_col])
        
        # Normalisation des formats d'email
        if 'email' in df.columns:
            df['email'] = df['email'].str.lower().str.strip()
        
        # Normalisation des numéros de téléphone
        if 'phone' in df.columns:
            df['phone'] = df['phone'].apply(lambda x: self._normalize_phone(x) if isinstance(x, str) else x)
        
        # Normalisation des noms et prénoms (capitalisation)
        for col in ['first_name', 'last_name']:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: x.title() if isinstance(x, str) else x)
        
        # Normalisation des noms de pays
        if 'country' in df.columns:
            country_mapping = rules.get('country_mapping', {})
            if country_mapping:
                df['country'] = df['country'].apply(
                    lambda x: country_mapping.get(x.lower(), x) if isinstance(x, str) else x
                )
        
        return df
    
    def _normalize_phone(self, phone):
        """
        Normalise un numéro de téléphone en format standard.
        
        Args:
            phone: Numéro de téléphone à normaliser
            
        Returns:
            str: Numéro de téléphone normalisé
        """
        if not phone:
            return phone
            
        # Supprimer tous les caractères non numériques
        digits_only = re.sub(r'\D', '', phone)
        
        # Si le numéro est trop court ou trop long, le laisser tel quel
        if len(digits_only) < 7 or len(digits_only) > 15:
            return phone
            
        # Format international pour les numéros sans préfixe international
        if not digits_only.startswith('00') and not digits_only.startswith('+'):
            # On suppose que c'est un numéro sans indicatif international
            if len(digits_only) == 10 and digits_only.startswith('0'):
                # Format français: transformer 0X XX XX XX XX en +33 X XX XX XX XX
                return f"+33 {digits_only[1:3]} {digits_only[3:5]} {digits_only[5:7]} {digits_only[7:9]} {digits_only[9:]}"
            else:
                # Autre format, on le laisse tel quel avec espaces tous les 2 chiffres
                return ' '.join(digits_only[i:i+2] for i in range(0, len(digits_only), 2))
        
        # Format international déjà présent
        if digits_only.startswith('00'):
            # Convertir 00XX en +XX
            return f"+{digits_only[2:4]} {digits_only[4:6]} {digits_only[6:8]} {digits_only[8:10]} {digits_only[10:]}"
        
        # Déjà au format +XX, ajouter des espaces
        return f"+{digits_only[1:3]} {digits_only[3:5]} {digits_only[5:7]} {digits_only[7:9]} {digits_only[9:]}"
    
    def _clean_data(self, df, rules):
        """
        Nettoie les données selon les règles spécifiées.
        
        Args:
            df: DataFrame des leads
            rules: Règles de nettoyage
            
        Returns:
            DataFrame: DataFrame avec données nettoyées
        """
        # Copie pour éviter de modifier l'original
        cleaned_df = df.copy()
        
        # Suppression des espaces superflus
        for col in cleaned_df.columns:
            if cleaned_df[col].dtype == 'object':
                cleaned_df[col] = cleaned_df[col].apply(
                    lambda x: x.strip() if isinstance(x, str) else x
                )
        
        # Nettoyage des emails
        if 'email' in cleaned_df.columns:
            # Vérifier le format des emails
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            cleaned_df['valid_email'] = cleaned_df['email'].apply(
                lambda x: bool(re.match(email_pattern, str(x))) if x else False
            )
            
            # Nettoyer les emails invalides
            invalid_email_mask = ~cleaned_df['valid_email'] & cleaned_df['email'].notna()
            cleaned_df.loc[invalid_email_mask, 'email'] = cleaned_df.loc[invalid_email_mask, 'email'].apply(
                lambda x: self._clean_email(x)
            )
            
            # Vérifier à nouveau la validité
            cleaned_df['valid_email'] = cleaned_df['email'].apply(
                lambda x: bool(re.match(email_pattern, str(x))) if x else False
            )
        
        # Suppression des caractères spéciaux indésirables dans les noms
        for col in ['first_name', 'last_name']:
            if col in cleaned_df.columns:
                cleaned_df[col] = cleaned_df[col].apply(
                    lambda x: re.sub(r'[^a-zA-ZÀ-ÿ\s\-\']', '', str(x)) if isinstance(x, str) else x
                )
        
        # Nettoyage du nom d'entreprise
        if 'company' in cleaned_df.columns:
            # Supprimer les suffixes légaux courants
            company_suffixes = rules.get('company_suffixes', ['Inc.', 'LLC', 'Ltd', 'Corp.', 'SA', 'SAS', 'SARL', 'GmbH'])
            for suffix in company_suffixes:
                cleaned_df['company'] = cleaned_df['company'].apply(
                    lambda x: re.sub(rf'\s*{re.escape(suffix)}\s*$', '', str(x)) if isinstance(x, str) else x
                )
        
        # Appliquer les règles de nettoyage personnalisées
        custom_cleaning_rules = rules.get('custom_cleaning', {})
        for col, rule in custom_cleaning_rules.items():
            if col in cleaned_df.columns and 'regex' in rule and 'replacement' in rule:
                cleaned_df[col] = cleaned_df[col].apply(
                    lambda x: re.sub(rule['regex'], rule['replacement'], str(x)) if isinstance(x, str) else x
                )
        
        # Suppression des colonnes temporaires
        if 'valid_email' in cleaned_df.columns:
            cleaned_df = cleaned_df.drop(columns=['valid_email'])
        
        return cleaned_df
    
    def _clean_email(self, email):
        """
        Tente de nettoyer un email potentiellement invalide.
        
        Args:
            email: Email à nettoyer
            
        Returns:
            str: Email nettoyé ou chaîne vide si non récupérable
        """
        if not email or not isinstance(email, str):
            return ""
        
        # Supprimer les espaces
        email = email.strip().lower()
        
        # Corriger les erreurs courantes
        email = email.replace(" at ", "@").replace(" dot ", ".")
        email = re.sub(r'\s+', '', email)  # Supprimer tous les espaces
        
        # Vérifier si l'email a un format valide après nettoyage
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(email_pattern, email):
            return email
        else:
            # Tentative de correction pour les erreurs communes
            # Vérifier s'il y a un @ dans l'email
            if '@' not in email:
                return ""
            
            # Vérifier s'il manque le point dans le domaine
            parts = email.split('@')
            if len(parts) != 2:
                return ""
            
            local, domain = parts
            if '.' not in domain:
                # Essayer de deviner le TLD
                common_tlds = ['.com', '.org', '.net', '.io', '.fr', '.de', '.uk']
                for tld in common_tlds:
                    if domain.endswith(tld[1:]):
                        domain = domain[:-len(tld[1:])] + tld
                        break
                else:
                    # Aucun TLD connu trouvé, ajouter .com par défaut
                    domain += '.com'
            
            corrected_email = f"{local}@{domain}"
            # Vérifier une dernière fois
            if re.match(email_pattern, corrected_email):
                return corrected_email
            else:
                return ""
    
    def _deduplicate(self, df, rules):
        """
        Supprime les doublons selon les règles spécifiées.
        
        Args:
            df: DataFrame des leads
            rules: Règles de nettoyage
            
        Returns:
            DataFrame: DataFrame sans doublons
        """
        # Copie pour éviter de modifier l'original
        dedup_df = df.copy()
        
        # Définir les colonnes pour la déduplication
        dedup_columns = rules.get('deduplication_fields', ['email', 'phone'])
        
        # Filtrer pour ne garder que les colonnes existantes
        dedup_columns = [col for col in dedup_columns if col in dedup_df.columns]
        
        if not dedup_columns:
            # Pas de colonnes pour dédupliquer, retourner tel quel
            return dedup_df
        
        # Marquer les doublons
        for col in dedup_columns:
            if col in dedup_df.columns:
                # Ignorer les valeurs vides ou NA
                mask = dedup_df[col].notna() & (dedup_df[col] != '')
                dedup_df[f'dup_{col}'] = False
                dedup_df.loc[mask, f'dup_{col}'] = dedup_df.loc[mask].duplicated(subset=[col])
        
        # Un lead est un doublon s'il est marqué comme tel dans n'importe quelle colonne
        duplicate_mask = False
        for col in dedup_columns:
            if f'dup_{col}' in dedup_df.columns:
                duplicate_mask = duplicate_mask | dedup_df[f'dup_{col}']
        
        # Filtrer les non-doublons
        dedup_df = dedup_df[~duplicate_mask]
        
        # Supprimer les colonnes temporaires
        for col in dedup_columns:
            if f'dup_{col}' in dedup_df.columns:
                dedup_df = dedup_df.drop(columns=[f'dup_{col}'])
        
        return dedup_df
    
    def _validate_leads(self, df, rules):
        """
        Valide les leads selon les règles spécifiées.
        
        Args:
            df: DataFrame des leads
            rules: Règles de validation
            
        Returns:
            tuple: (DataFrame des leads valides, DataFrame des leads invalides)
        """
        # Copie pour éviter de modifier l'original
        validate_df = df.copy()
        
        # Définir les règles de validation
        validation_rules = rules.get('validation', {
            'required_fields': ['email', 'first_name', 'last_name'],
            'email_validation': True,
            'phone_validation': True,
            'domain_blacklist': []
        })
        
        # Initialiser le masque de validation
        valid_mask = pd.Series(True, index=validate_df.index)
        
        # Valider les champs requis
        required_fields = validation_rules.get('required_fields', [])
        for field in required_fields:
            if field in validate_df.columns:
                valid_mask = valid_mask & validate_df[field].notna() & (validate_df[field] != '')
        
        # Valider les emails
        if validation_rules.get('email_validation', True) and 'email' in validate_df.columns:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            valid_mask = valid_mask & validate_df['email'].apply(
                lambda x: bool(re.match(email_pattern, str(x))) if x else False
            )
            
            # Vérifier les domaines blacklistés
            domain_blacklist = validation_rules.get('domain_blacklist', [])
            if domain_blacklist and 'email' in validate_df.columns:
                email_domain = validate_df['email'].apply(
                    lambda x: x.split('@')[1].lower() if isinstance(x, str) and '@' in x else ''
                )
                valid_mask = valid_mask & ~email_domain.isin(domain_blacklist)
        
        # Valider les numéros de téléphone
        if validation_rules.get('phone_validation', True) and 'phone' in validate_df.columns:
            # Un numéro est valide s'il a au moins 7 chiffres
            valid_mask = valid_mask & (
                (validate_df['phone'].isna()) |  # Phone peut être null
                (validate_df['phone'].apply(
                    lambda x: len(re.sub(r'\D', '', str(x))) >= 7 if isinstance(x, str) else False
                ))
            )
        
        # Séparer les leads valides et invalides
        valid_df = validate_df[valid_mask].copy()
        invalid_df = validate_df[~valid_mask].copy()
        
        return valid_df, invalid_df
    
    def _count_normalized_fields(self, original_df, normalized_df):
        """
        Compte le nombre de champs normalisés.
        
        Args:
            original_df: DataFrame original
            normalized_df: DataFrame normalisé
            
        Returns:
            int: Nombre de champs normalisés
        """
        # Compter les différences de noms de colonnes
        orig_cols = set(original_df.columns)
        norm_cols = set(normalized_df.columns)
        
        # Les colonnes qui existent dans l'un mais pas dans l'autre
        changed_cols = len((orig_cols - norm_cols) | (norm_cols - orig_cols))
        
        return changed_cols
    
    def _save_cleaned_leads(self, cleaned_leads, campaign_id, source):
        """
        Enregistre les leads nettoyés dans la base de données.
        
        Args:
            cleaned_leads: Liste des leads nettoyés
            campaign_id: ID de la campagne
            source: Source des leads
        """
        try:
            # Préparer les données pour l'insertion
            lead_records = []
            for lead in cleaned_leads:
                lead_data = {
                    'campaign_id': campaign_id,
                    'source': source,
                    'created_at': datetime.utcnow(),
                    'updated_at': datetime.utcnow(),
                    'status': 'new',
                    'is_cleaned': True,
                    'data': json.dumps(lead)
                }
                
                # Extraire les champs principaux s'ils existent
                for field in ['email', 'first_name', 'last_name', 'phone', 'company', 'job_title']:
                    if field in lead:
                        lead_data[field] = lead[field]
                
                lead_records.append(lead_data)
            
            # Insérer en masse
            if lead_records:
                self.db.execute(LeadModel.__table__.insert(), lead_records)
                self.db.commit()
                
                self.logger.info(f"{len(lead_records)} leads nettoyés enregistrés pour la campagne {campaign_id}")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'enregistrement des leads nettoyés: {str(e)}")
            self.db.rollback()
    
    def store_feedback(self, cleaning_job_id, feedback):
        """
        Stocke le feedback sur un job de nettoyage.
        
        Args:
            cleaning_job_id: ID du job de nettoyage
            feedback: Données de feedback
            
        Returns:
            bool: Succès de l'opération
        """
        try:
            # Récupérer le log
            log_entry = self.db.query(AgentLog).filter(
                AgentLog.id == cleaning_job_id
            ).first()
            
            if not log_entry:
                self.logger.error(f"Log de nettoyage avec ID {cleaning_job_id} non trouvé")
                return False
            
            # Mettre à jour avec le feedback
            log_entry.feedback_score = feedback.get('score')
            log_entry.feedback_text = feedback.get('text')
            log_entry.feedback_timestamp = datetime.utcnow()
            
            self.db.commit()
            
            # Log le feedback
            self.logger.info(f"Feedback enregistré pour le job de nettoyage {cleaning_job_id}: Score {feedback.get('score')}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors du stockage du feedback: {str(e)}")
            self.db.rollback()
            return False
