from datetime import datetime
import time
import json
import re
from typing import Dict, Any, List, Optional
import logging
import pandas as pd
import numpy as np

from .base import BaseAgent
from .utils.llm import ask_llm, generate_structured_response
from .utils.vectorstore import VectorStore

class LeadClassifierAgent(BaseAgent):
    """
    Agent responsable de la classification et du scoring des leads.
    
    Cet agent analyse les leads pour déterminer leur potentiel,
    leur pertinence pour la campagne et leur probabilité de conversion.
    """
    
    def __init__(self, agent_id, db_session):
        super().__init__(agent_id, db_session)
        self.vector_store = None
        
        # Initialiser le vectorstore si configuré dans les paramètres de l'agent
        if self.agent_model and self.agent_model.configuration.get("use_vectorstore", False):
            collection_name = self.agent_model.configuration.get("vectorstore_collection", "lead_classifications")
            self.vector_store = VectorStore(collection_name=collection_name)
    
    def run(self, input_data):
        """
        Exécute l'agent de classification des leads.
        
        Args:
            input_data (dict): Les données d'entrée, qui peuvent inclure:
                - leads: Liste des leads à classifier
                - campaign_id: ID de la campagne
                - rules: Règles de classification
                - scoring_model: Modèle de scoring à utiliser
                - threshold: Seuil pour considérer un lead comme qualifié
                
        Returns:
            dict: Résultats de la classification
        """
        self.logger.info(f"Lancement de LeadClassifierAgent avec {len(input_data.get('leads', []))} leads")
        
        start_time = time.time()
        
        try:
            # Extraire les paramètres
            leads = input_data.get('leads', [])
            campaign_id = input_data.get('campaign_id')
            rules = input_data.get('rules', {})
            scoring_model = input_data.get('scoring_model', 'default')
            threshold = input_data.get('threshold', 0.6)
            
            if not leads:
                return {
                    'status': 'error',
                    'message': 'Aucun lead à classifier',
                    'classified_leads': []
                }
            
            # Récupérer les informations de la campagne si disponible
            campaign_info = None
            if campaign_id:
                campaign_info = self._get_campaign_info(campaign_id)
            
            # Convertir les leads en DataFrame pour faciliter le traitement
            leads_df = pd.DataFrame(leads)
            
            # Classification et scoring des leads
            classified_leads = self._classify_leads(
                leads_df=leads_df,
                campaign_info=campaign_info,
                rules=rules,
                scoring_model=scoring_model,
                threshold=threshold
            )
            
            # Enregistrer les classifications dans la base de données
            if campaign_id:
                self._save_classifications(classified_leads, campaign_id)
            
            # Stocker les classifications dans le vectorstore si configuré
            if self.vector_store and classified_leads:
                self._store_classifications_in_vectorstore(classified_leads, campaign_id)
            
            execution_time = time.time() - start_time
            
            # Calculer des statistiques sur les classifications
            stats = self._calculate_statistics(classified_leads)
            
            # Préparer les résultats
            results = {
                'status': 'success',
                'message': f"Classification terminée: {len(classified_leads)} leads traités",
                'classified_leads': classified_leads,
                'stats': stats,
                'execution_time': execution_time
            }
            
            # Logging des résultats
            self.log_execution(
                operation="classify_leads",
                input_data={'lead_count': len(leads), 'campaign_id': campaign_id, 'model': scoring_model},
                output_data=results,
                status="success",
                execution_time=execution_time
            )
            
            return results
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Erreur lors de l'exécution de LeadClassifierAgent: {str(e)}")
            
            # Logging de l'erreur
            self.log_execution(
                operation="classify_leads",
                input_data=input_data,
                output_data={"error": str(e)},
                status="error",
                execution_time=execution_time
            )
            
            return {
                'status': 'error',
                'message': str(e),
                'classified_leads': []
            }
    
    def _get_campaign_info(self, campaign_id):
        """
        Récupère les informations de la campagne.
        
        Args:
            campaign_id: ID de la campagne
            
        Returns:
            dict: Informations de la campagne
        """
        try:
            # Récupérer la campagne
            campaign = self.db.query(CampaignModel).filter(CampaignModel.id == campaign_id).first()
            
            if not campaign:
                raise ValueError(f"Campagne avec ID {campaign_id} non trouvée")
            
            # Récupérer le profil cible de la campagne
            target_profile = self.db.query(TargetProfileModel).filter(
                TargetProfileModel.campaign_id == campaign_id
            ).first()
            
            # Récupérer les dernières analyses de la campagne
            campaign_analysis = self.db.query(CampaignAnalysisModel).filter(
                CampaignAnalysisModel.campaign_id == campaign_id
            ).order_by(CampaignAnalysisModel.created_at.desc()).first()
            
            # Assembler les informations
            campaign_info = {
                'id': campaign.id,
                'name': campaign.name,
                'niche': campaign.niche,
                'target_audience': campaign.target_audience,
                'goals': campaign.goals,
                'target_profile': target_profile.profile_data if target_profile else {},
                'recent_analysis': campaign_analysis.analysis_data if campaign_analysis else {}
            }
            
            return campaign_info
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des informations de campagne: {str(e)}")
            return {}
    
    def _classify_leads(self, leads_df, campaign_info, rules, scoring_model, threshold):
        """
        Classifie et score les leads.
        
        Args:
            leads_df: DataFrame des leads
            campaign_info: Informations de la campagne
            rules: Règles de classification
            scoring_model: Modèle de scoring à utiliser
            threshold: Seuil pour considérer un lead comme qualifié
            
        Returns:
            list: Liste des leads classifiés
        """
        # Sélectionner le modèle de scoring approprié
        if scoring_model == 'llm':
            return self._classify_with_llm(leads_df, campaign_info, threshold)
        elif scoring_model == 'rules':
            return self._classify_with_rules(leads_df, campaign_info, rules, threshold)
        else:
            # Modèle par défaut: combinaison de règles et scoring heuristique
            return self._classify_with_hybrid(leads_df, campaign_info, rules, threshold)
    
    def _classify_with_rules(self, leads_df, campaign_info, rules, threshold):
        """
        Classifie les leads selon des règles prédéfinies.
        
        Args:
            leads_df: DataFrame des leads
            campaign_info: Informations de la campagne
            rules: Règles de classification
            threshold: Seuil pour considérer un lead comme qualifié
            
        Returns:
            list: Liste des leads classifiés
        """
        # Copie pour éviter de modifier l'original
        df = leads_df.copy()
        
        # Initialiser les colonnes de score
        df['score'] = 0.0
        df['category'] = 'unqualified'
        df['reasons'] = df.apply(lambda x: [], axis=1)
        
        # Charger les règles
        scoring_rules = rules.get('scoring_rules', [])
        if not scoring_rules:
            # Règles par défaut
            scoring_rules = [
                # Règles basées sur le poste
                {'field': 'job_title', 'contains': ['CEO', 'CTO', 'CFO', 'COO', 'Director', 'VP', 'Head', 'Chief'], 'score': 0.2, 'reason': 'Decision maker position'},
                {'field': 'job_title', 'contains': ['Manager', 'Lead', 'Senior'], 'score': 0.1, 'reason': 'Management position'},
                
                # Règles basées sur l'entreprise
                {'field': 'company_size', 'min': 100, 'max': 1000, 'score': 0.1, 'reason': 'Mid-size company'},
                {'field': 'company_size', 'min': 1000, 'score': 0.2, 'reason': 'Large company'},
                
                # Règles basées sur l'email
                {'field': 'email', 'regex': r'^[^@]+@[^@]+\.(com|org|net|edu|gov)$', 'score': 0.05, 'reason': 'Valid professional email domain'},
                {'field': 'email', 'not_contains': ['gmail.com', 'yahoo.com', 'hotmail.com'], 'score': 0.05, 'reason': 'Corporate email'},
                
                # Règles basées sur la complétude du profil
                {'field': 'completeness', 'min': 0.8, 'score': 0.1, 'reason': 'Complete profile'}
            ]
        
        # Calculer la complétude du profil
        important_fields = ['first_name', 'last_name', 'email', 'phone', 'company', 'job_title']
        df['completeness'] = df[important_fields].notna().mean(axis=1)
        
        # Appliquer chaque règle
        for rule in scoring_rules:
            # Récupérer le champ concerné
            field = rule.get('field')
            
            if field not in df.columns and field != 'completeness':
                continue
            
            # Initialiser le masque pour cette règle
            rule_mask = pd.Series(False, index=df.index)
            
            # Appliquer les différents types de règles
            if 'equals' in rule:
                rule_mask = df[field] == rule['equals']
            
            elif 'contains' in rule:
                contains_values = rule['contains']
                for value in contains_values:
                    if pd.api.types.is_string_dtype(df[field]):
                        rule_mask = rule_mask | df[field].str.contains(value, case=False, na=False)
            
            elif 'not_contains' in rule:
                not_contains_values = rule['not_contains']
                rule_mask = ~df[field].isna()  # Initialiser avec True pour les valeurs non-NA
                for value in not_contains_values:
                    if pd.api.types.is_string_dtype(df[field]):
                        rule_mask = rule_mask & ~df[field].str.contains(value, case=False, na=False)
            
            elif 'regex' in rule:
                if pd.api.types.is_string_dtype(df[field]):
                    rule_mask = df[field].str.match(rule['regex'], na=False)
            
            elif 'min' in rule or 'max' in rule:
                if 'min' in rule:
                    rule_mask = df[field] >= rule['min']
                if 'max' in rule:
                    max_mask = df[field] <= rule['max']
                    rule_mask = rule_mask & max_mask if 'min' in rule else max_mask
            
            # Appliquer le score et la raison
            df.loc[rule_mask, 'score'] += rule.get('score', 0.0)
            
            # Ajouter la raison pour les leads qui correspondent
            for idx in df[rule_mask].index:
                df.at[idx, 'reasons'] = df.at[idx, 'reasons'] + [rule.get('reason', 'Matched rule')]
        
        # Catégoriser les leads selon le score
        df.loc[df['score'] >= threshold, 'category'] = 'qualified'
        df.loc[(df['score'] < threshold) & (df['score'] >= threshold * 0.7), 'category'] = 'nurturing'
        df.loc[df['score'] < threshold * 0.7, 'category'] = 'unqualified'
        
        # Formater les résultats
        classified_leads = []
        for _, row in df.iterrows():
            lead = row.to_dict()
            
            # Nettoyer les champs calculés
            if 'completeness' in lead:
                del lead['completeness']
            
            # S'assurer que reasons est une liste
            if 'reasons' in lead and not isinstance(lead['reasons'], list):
                lead['reasons'] = [lead['reasons']]
            
            # Ajouter le timestamp
            lead['classified_at'] = datetime.utcnow().isoformat()
            
            classified_leads.append(lead)
        
        return classified_leads
    
    def _classify_with_llm(self, leads_df, campaign_info, threshold):
        """
        Classifie les leads en utilisant un modèle de langage.
        
        Args:
            leads_df: DataFrame des leads
            campaign_info: Informations de la campagne
            threshold: Seuil pour considérer un lead comme qualifié
            
        Returns:
            list: Liste des leads classifiés
        """
        # Structure du schéma pour les résultats de classification
        classification_schema = {
            "classification": {
                "score": 0.85,  # Score entre 0 et 1
                "category": "qualified",  # qualified, nurturing, ou unqualified
                "reasons": ["Raison 1", "Raison 2"],
                "fit_score": 0.8,  # Adéquation avec la cible
                "interest_score": 0.7,  # Intérêt potentiel
                "authority_score": 0.9  # Pouvoir de décision
            }
        }
        
        classified_leads = []
        
        # Traiter chaque lead individuellement avec le LLM
        for _, lead in leads_df.iterrows():
            lead_dict = lead.to_dict()
            
            # Construire le prompt pour le LLM
            prompt = self._build_classification_prompt(lead_dict, campaign_info)
            
            # Appeler le LLM
            response = generate_structured_response(
                prompt=prompt,
                schema=classification_schema,
                system_message="Tu es un expert en qualification de leads B2B qui analyse le potentiel et l'adéquation des prospects.",
                model="gpt-4.1"
            )
            
            # Extraire la classification
            if "classification" in response:
                classification = response["classification"]
                
                # Appliquer le seuil pour vérifier la catégorie
                if classification.get('score', 0) >= threshold:
                    classification['category'] = 'qualified'
                elif classification.get('score', 0) >= threshold * 0.7:
                    classification['category'] = 'nurturing'
                else:
                    classification['category'] = 'unqualified'
                
                # Fusionner les données du lead avec la classification
                classified_lead = {**lead_dict, **classification}
                
                # Ajouter le timestamp
                classified_lead['classified_at'] = datetime.utcnow().isoformat()
                
                classified_leads.append(classified_lead)
            else:
                # Classification par défaut si le LLM échoue
                default_classification = {
                    'score': 0.0,
                    'category': 'unqualified',
                    'reasons': ['Classification failed'],
                    'classified_at': datetime.utcnow().isoformat()
                }
                classified_leads.append({**lead_dict, **default_classification})
                
                self.logger.warning(f"Échec de la classification LLM pour un lead")
        
        return classified_leads
    
    def _build_classification_prompt(self, lead, campaign_info):
        """
        Construit le prompt pour la classification LLM.
        
        Args:
            lead: Données du lead
            campaign_info: Informations de la campagne
            
        Returns:
            str: Prompt pour le LLM
        """
        # Formater les données du lead
        lead_str = "\n".join([f"{k}: {v}" for k, v in lead.items() if v and k not in ['score', 'category', 'reasons']])
        
        # Formater les informations de la campagne
        campaign_str = ""
        if campaign_info:
            campaign_str = f"""
            Campagne: {campaign_info.get('name', 'N/A')}
            Niche: {campaign_info.get('niche', 'N/A')}
            Audience cible: {campaign_info.get('target_audience', 'N/A')}
            Objectifs: {campaign_info.get('goals', 'N/A')}
            """
            
            # Ajouter le profil cible si disponible
            target_profile = campaign_info.get('target_profile', {})
            if target_profile:
                campaign_str += "\nProfil cible:\n"
                campaign_str += "\n".join([f"- {k}: {v}" for k, v in target_profile.items()])
        
        # Construire le prompt complet
        prompt = f"""
        Analyse ce lead par rapport à la campagne spécifiée et détermine sa qualité, son potentiel et son adéquation.
        
        Informations sur le lead:
        {lead_str}
        
        Informations sur la campagne:
        {campaign_str}
        
        Effectue une évaluation complète, puis attribue:
        1. Un score global entre 0 et 1
        2. Une catégorie (qualified, nurturing, unqualified)
        3. Des raisons spécifiques justifiant ton évaluation
        4. Un score d'adéquation avec la cible (fit_score)
        5. Un score d'intérêt potentiel (interest_score)
        6. Un score de pouvoir de décision (authority_score)
        
        Base ton analyse sur:
        - L'adéquation du poste/fonction avec le profil cible
        - La taille et l'industrie de l'entreprise
        - La complétude et la qualité des informations
        - Le niveau hiérarchique et le pouvoir de décision probable
        """
        
        return prompt
    
    def _classify_with_hybrid(self, leads_df, campaign_info, rules, threshold):
        """
        Classifie les leads avec une approche hybride (règles + heuristiques).
        
        Args:
            leads_df: DataFrame des leads
            campaign_info: Informations de la campagne
            rules: Règles de classification
            threshold: Seuil pour considérer un lead comme qualifié
            
        Returns:
            list: Liste des leads classifiés
        """
        # Commencer par la classification basée sur les règles
        rule_classified = self._classify_with_rules(leads_df, campaign_info, rules, threshold)
        
        # Ajouter des scores supplémentaires basés sur des heuristiques
        for lead in rule_classified:
            # Score d'adéquation avec la cible
            lead['fit_score'] = self._calculate_fit_score(lead, campaign_info)
            
            # Score d'intérêt potentiel
            lead['interest_score'] = self._calculate_interest_score(lead, campaign_info)
            
            # Score de pouvoir de décision
            lead['authority_score'] = self._calculate_authority_score(lead)
            
            # Ajuster le score global en fonction des nouveaux scores
            original_score = lead.get('score', 0.0)
            weighted_score = (
                original_score * 0.4 +
                lead['fit_score'] * 0.3 +
                lead['interest_score'] * 0.15 +
                lead['authority_score'] * 0.15
            )
            
            # Mettre à jour le score et la catégorie
            lead['score'] = min(1.0, weighted_score)  # Plafonner à 1.0
            
            # Recatégoriser
            if lead['score'] >= threshold:
                lead['category'] = 'qualified'
            elif lead['score'] >= threshold * 0.7:
                lead['category'] = 'nurturing'
            else:
                lead['category'] = 'unqualified'
        
        return rule_classified
    
    def _calculate_fit_score(self, lead, campaign_info):
        """
        Calcule le score d'adéquation avec la cible.
        
        Args:
            lead: Données du lead
            campaign_info: Informations de la campagne
            
        Returns:
            float: Score d'adéquation
        """
        fit_score = 0.5  # Score par défaut
        
        # Si pas d'infos campagne, retourner le score par défaut
        if not campaign_info:
            return fit_score
        
        target_profile = campaign_info.get('target_profile', {})
        
        # Vérifier l'industrie
        if 'industry' in lead and 'target_industries' in target_profile:
            target_industries = target_profile['target_industries']
            if isinstance(target_industries, list) and lead['industry'] in target_industries:
                fit_score += 0.2
            elif isinstance(target_industries, str) and lead['industry'] == target_industries:
                fit_score += 0.2
        
        # Vérifier la taille de l'entreprise
        if 'company_size' in lead and 'target_company_size' in target_profile:
            target_size = target_profile['target_company_size']
            if isinstance(target_size, dict):
                min_size = target_size.get('min', 0)
                max_size = target_size.get('max', float('inf'))
                if min_size <= lead['company_size'] <= max_size:
                    fit_score += 0.15
        
        # Vérifier la fonction/le poste
        if 'job_title' in lead and 'target_roles' in target_profile:
            target_roles = target_profile['target_roles']
            if isinstance(target_roles, list):
                for role in target_roles:
                    if role.lower() in lead['job_title'].lower():
                        fit_score += 0.15
                        break
        
        # Vérifier la localisation
        if 'country' in lead and 'target_regions' in target_profile:
            target_regions = target_profile['target_regions']
            if isinstance(target_regions, list) and lead['country'] in target_regions:
                fit_score += 0.1
        
        # Plafonner le score à 1.0
        return min(1.0, fit_score)
    
    def _calculate_interest_score(self, lead, campaign_info):
        """
        Calcule le score d'intérêt potentiel.
        
        Args:
            lead: Données du lead
            campaign_info: Informations de la campagne
            
        Returns:
            float: Score d'intérêt
        """
        interest_score = 0.4  # Score par défaut
        
        # Bonifier si le lead a des interactions précédentes
        if 'previous_interactions' in lead:
            interactions = lead['previous_interactions']
            if isinstance(interactions, list) and interactions:
                # Donner plus de poids aux interactions récentes
                recent_interactions = [i for i in interactions if i.get('timestamp') and 
                                      (datetime.utcnow() - datetime.fromisoformat(i['timestamp'])).days < 30]
                if recent_interactions:
                    interest_score += 0.3
                else:
                    interest_score += 0.1
        
        # Bonifier si le lead a des visites de site
        if 'website_visits' in lead:
            visits = lead['website_visits']
            if isinstance(visits, list) and visits:
                interest_score += min(0.2, len(visits) * 0.05)  # Max 0.2
        
        # Bonifier si le lead a ouvert des emails précédents
        if 'email_opens' in lead and lead['email_opens'] > 0:
            interest_score += min(0.2, lead['email_opens'] * 0.04)  # Max 0.2
        
        # Bonifier si le lead a cliqué sur des liens
        if 'email_clicks' in lead and lead['email_clicks'] > 0:
            interest_score += min(0.3, lead['email_clicks'] * 0.1)  # Max 0.3
        
        # Plafonner le score à 1.0
        return min(1.0, interest_score)
    
    def _calculate_authority_score(self, lead):
        """
        Calcule le score de pouvoir de décision.
        
        Args:
            lead: Données du lead
            
        Returns:
            float: Score de pouvoir de décision
        """
        authority_score = 0.3  # Score par défaut
        
        # Analyser le titre/poste
        if 'job_title' in lead and lead['job_title']:
            job_title = lead['job_title'].lower()
            
            # Haute autorité
            high_authority = ['ceo', 'cto', 'cfo', 'coo', 'president', 'owner', 'founder', 
                             'chief', 'director', 'vp', 'vice president', 'head']
            
            # Autorité moyenne
            mid_authority = ['manager', 'lead', 'senior', 'principal', 'consultant', 'architect']
            
            for title in high_authority:
                if title in job_title:
                    authority_score = 0.9
                    break
                    
            if authority_score < 0.9:  # Si pas déjà identifié comme haute autorité
                for title in mid_authority:
                    if title in job_title:
                        authority_score = 0.6
                        break
        
        # Bonifier si c'est un employé qui a longtemps dans l'entreprise
        if 'years_in_company' in lead and isinstance(lead['years_in_company'], (int, float)):
            authority_score += min(0.2, lead['years_in_company'] * 0.02)  # Max 0.2
        
        # Plafonner le score à 1.0
        return min(1.0, authority_score)
    
    def _save_classifications(self, classified_leads, campaign_id):
        """
        Enregistre les classifications dans la base de données.
        
        Args:
            classified_leads: Liste des leads classifiés
            campaign_id: ID de la campagne
        """
        try:
            # Préparer les données pour l'insertion
            classification_records = []
            for lead in classified_leads:
                # Extraire l'ID du lead si disponible
                lead_id = lead.get('id')
                if not lead_id:
                    # Si l'ID n'est pas disponible, essayer de trouver le lead par email
                    email = lead.get('email')
                    if email:
                        lead_db = self.db.query(LeadModel).filter(
                            LeadModel.campaign_id == campaign_id,
                            LeadModel.email == email
                        ).first()
                        if lead_db:
                            lead_id = lead_db.id
                
                # Si on n'a pas pu identifier le lead, passer au suivant
                if not lead_id:
                    continue
                
                # Préparer les données de classification
                classification_data = {
                    'lead_id': lead_id,
                    'campaign_id': campaign_id,
                    'score': lead.get('score', 0.0),
                    'category': lead.get('category', 'unqualified'),
                    'fit_score': lead.get('fit_score', 0.0),
                    'interest_score': lead.get('interest_score', 0.0),
                    'authority_score': lead.get('authority_score', 0.0),
                    'reasons': json.dumps(lead.get('reasons', [])),
                    'created_at': datetime.utcnow()
                }
                
                classification_records.append(classification_data)
            
            # Insérer en masse
            if classification_records:
                self.db.execute(LeadClassificationModel.__table__.insert(), classification_records)
                self.db.commit()
                
                self.logger.info(f"{len(classification_records)} classifications enregistrées pour la campagne {campaign_id}")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'enregistrement des classifications: {str(e)}")
            self.db.rollback()
    
    def _store_classifications_in_vectorstore(self, classified_leads, campaign_id):
        """
        Stocke les classifications dans le vectorstore pour référence future.
        
        Args:
            classified_leads: Liste des leads classifiés
            campaign_id: ID de la campagne
        """
        if not self.vector_store:
            return
            
        try:
            for lead in classified_leads:
                # Préparer le texte à vectoriser
                lead_text = f"""
                Lead: {lead.get('first_name', '')} {lead.get('last_name', '')}
                Email: {lead.get('email', '')}
                Company: {lead.get('company', '')}
                Job Title: {lead.get('job_title', '')}
                Industry: {lead.get('industry', '')}
                Score: {lead.get('score', 0.0)}
                Category: {lead.get('category', '')}
                Reasons: {', '.join(lead.get('reasons', []))}
                """
                
                # Préparer les métadonnées
                metadata = {
                    'lead_email': lead.get('email', ''),
                    'campaign_id': campaign_id,
                    'score': lead.get('score', 0.0),
                    'category': lead.get('category', ''),
                    'classified_at': lead.get('classified_at', datetime.utcnow().isoformat())
                }
                
                # Ajouter au vectorstore
                self.vector_store.add_text(
                    text=lead_text,
                    metadata=metadata
                )
                
        except Exception as e:
            self.logger.error(f"Erreur lors du stockage des classifications dans le vectorstore: {str(e)}")
    
    def _calculate_statistics(self, classified_leads):
        """
        Calcule des statistiques sur les leads classifiés.
        
        Args:
            classified_leads: Liste des leads classifiés
            
        Returns:
            dict: Statistiques sur les classifications
        """
        if not classified_leads:
            return {
                'total': 0,
                'categories': {},
                'average_score': 0.0
            }
        
        # Initialiser les statistiques
        stats = {
            'total': len(classified_leads),
            'categories': {},
            'average_score': 0.0,
            'score_distribution': {
                'excellent': 0,  # >= 0.8
                'good': 0,       # >= 0.6 and < 0.8
                'average': 0,    # >= 0.4 and < 0.6
                'poor': 0        # < 0.4
            }
        }
        
        # Calculer les scores par catégorie
        category_counts = {}
        total_score = 0.0
        
        for lead in classified_leads:
            # Catégorie
            category = lead.get('category', 'unknown')
            if category not in category_counts:
                category_counts[category] = 0
            category_counts[category] += 1
            
            # Score
            score = lead.get('score', 0.0)
            total_score += score
            
            # Distribution de score
            if score >= 0.8:
                stats['score_distribution']['excellent'] += 1
            elif score >= 0.6:
                stats['score_distribution']['good'] += 1
            elif score >= 0.4:
                stats['score_distribution']['average'] += 1
            else:
                stats['score_distribution']['poor'] += 1
        
        # Calculer les pourcentages par catégorie
        for category, count in category_counts.items():
            stats['categories'][category] = {
                'count': count,
                'percentage': round((count / stats['total']) * 100, 1)
            }
        
        # Calculer le score moyen
        stats['average_score'] = round(total_score / stats['total'], 2) if stats['total'] > 0 else 0.0
        
        # Convertir les distributions en pourcentages
        for key in stats['score_distribution']:
            count = stats['score_distribution'][key]
            stats['score_distribution'][key] = {
                'count': count,
                'percentage': round((count / stats['total']) * 100, 1) if stats['total'] > 0 else 0.0
            }
        
        return stats
    
    def store_feedback(self, classification_id, feedback):
        """
        Stocke le feedback sur une classification.
        
        Args:
            classification_id: ID de la classification
            feedback: Données de feedback
            
        Returns:
            bool: Succès de l'opération
        """
        try:
            # Récupérer la classification
            classification = self.db.query(LeadClassificationModel).filter(
                LeadClassificationModel.id == classification_id
            ).first()
            
            if not classification:
                self.logger.error(f"Classification avec ID {classification_id} non trouvée")
                return False
            
            # Mettre à jour avec le feedback
            classification.feedback_score = feedback.get('score')
            classification.feedback_text = feedback.get('text')
            classification.feedback_timestamp = datetime.utcnow()
            
            # Si c'est une correction de catégorie
            if 'corrected_category' in feedback:
                classification.corrected_category = feedback['corrected_category']
                
                # Mettre à jour le lead si nécessaire
                if feedback.get('update_lead', False):
                    lead = self.db.query(LeadModel).filter(
                        LeadModel.id == classification.lead_id
                    ).first()
                    
                    if lead:
                        lead.category = feedback['corrected_category']
                        self.logger.info(f"Catégorie du lead {lead.id} mise à jour vers {feedback['corrected_category']}")
            
            self.db.commit()
            
            # Log le feedback
            self.logger.info(f"Feedback enregistré pour la classification {classification_id}: Score {feedback.get('score')}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors du stockage du feedback: {str(e)}")
            self.db.rollback()
            return False
