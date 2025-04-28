from datetime import datetime
import time
from typing import Dict, Any, List, Optional
import logging

from .base import BaseAgent
from .utils.llm import ask_llm, generate_structured_response

class StrategyAgent(BaseAgent):
    """
    Agent responsable de générer des stratégies et des niches de marché.
    
    Cet agent génère de nouvelles niches de marché basées sur des tendances,
    des données historiques, et les résultats précédents.
    """
    
    def __init__(self, agent_id, db_session):
        super().__init__(agent_id, db_session)
        self.rejected_niches = []  # Stockage temporaire des niches refusées
    
    def run(self, input_data):
        """
        Exécute l'agent de stratégie.
        
        Args:
            input_data (dict): Les données d'entrée, qui peuvent inclure:
                - campaign_id: ID de la campagne
                - market_data: Données de marché
                - constraints: Contraintes pour la génération de niches
                - count: Nombre de niches à générer
                
        Returns:
            dict: Résultats de l'exécution, incluant les niches générées
        """
        self.logger.info(f"Lancement de StrategyAgent avec données: {input_data}")
        
        start_time = time.time()
        
        try:
            # Extraire les paramètres
            campaign_id = input_data.get('campaign_id')
            market_data = input_data.get('market_data', {})
            constraints = input_data.get('constraints', {})
            count = input_data.get('count', 3)
            
            # Récupérer l'historique des niches précédentes (si disponible)
            previous_niches = self._get_previous_niches(campaign_id)
            
            # Générer des nouvelles niches
            generated_niches = self._generate_niches(
                market_data=market_data,
                constraints=constraints,
                previous_niches=previous_niches,
                count=count
            )
            
            # Préparer les résultats
            results = {
                'niches': generated_niches,
                'campaign_id': campaign_id,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            execution_time = time.time() - start_time
            
            # Logging des résultats
            self.log_execution(
                operation="generate_niches",
                input_data=input_data,
                output_data=results,
                status="success",
                execution_time=execution_time
            )
            
            return results
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Erreur lors de l'exécution de StrategyAgent: {str(e)}")
            
            # Logging de l'erreur
            self.log_execution(
                operation="generate_niches",
                input_data=input_data,
                output_data={"error": str(e)},
                status="error",
                execution_time=execution_time
            )
            
            return {"error": str(e)}
    
    def _get_previous_niches(self, campaign_id):
        """
        Récupère l'historique des niches pour une campagne.
        
        Args:
            campaign_id: ID de la campagne
            
        Returns:
            list: Liste des niches précédemment générées
        """
        if not campaign_id:
            return []
            
        try:
            # Requête à la base de données pour récupérer les niches précédentes
            # Cette implémentation dépendra de votre modèle de données
            query = """
                SELECT n.* FROM niches n
                JOIN campaigns c ON n.campaign_id = c.id
                WHERE c.id = :campaign_id
                ORDER BY n.created_at DESC
            """
            
            result = self.db.execute(query, {"campaign_id": campaign_id})
            niches = [dict(row) for row in result]
            
            # Ajouter les niches rejetées temporaires
            niches.extend(self.rejected_niches)
            
            return niches
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des niches précédentes: {str(e)}")
            return []
    
    def _generate_niches(self, market_data, constraints, previous_niches, count):
        """
        Génère de nouvelles niches de marché.
        
        Args:
            market_data (dict): Données de marché
            constraints (dict): Contraintes pour la génération
            previous_niches (list): Niches précédemment générées
            count (int): Nombre de niches à générer
            
        Returns:
            list: Liste des niches générées
        """
        # Structure du schéma attendu pour la réponse
        niche_schema = {
            "niches": [
                {
                    "name": "Nom de la niche",
                    "description": "Description détaillée",
                    "target_audience": "Public cible",
                    "market_size": "Taille estimée du marché",
                    "competition_level": "Niveau de compétition (1-10)",
                    "potential_score": "Score de potentiel (1-10)",
                    "keywords": ["mot-clé1", "mot-clé2", "..."]
                }
            ]
        }
        
        # Formater les niches précédentes pour éviter les duplications
        previous_niche_names = [n.get('name', '') for n in previous_niches]
        previous_niche_str = ", ".join(previous_niche_names)
        
        # Construire le prompt
        prompt = f"""
        En tant qu'expert en stratégie de marché, génère {count} nouvelles niches de marché innovantes.
        
        Données de marché:
        {market_data}
        
        Contraintes à respecter:
        {constraints}
        
        Niches précédemment générées (à éviter):
        {previous_niche_str}
        
        Pour chaque niche, fournis:
        1. Un nom concis et précis
        2. Une description détaillée
        3. Le public cible
        4. La taille estimée du marché
        5. Le niveau de compétition (1-10)
        6. Un score de potentiel (1-10)
        7. Des mots-clés pertinents
        
        Assure-toi que chaque niche soit:
        - Unique et différenciée des précédentes
        - Alignée avec les contraintes
        - Basée sur les données de marché fournies
        - Réaliste et exploitable
        """
        
        # Générer les niches via LLM
        response = generate_structured_response(
            prompt=prompt,
            schema=niche_schema,
            system_message="Tu es un expert en stratégie de marché et en identification de niches rentables.",
            model="gpt-4.1"  # Utiliser un modèle avancé pour cette tâche stratégique
        )
        
        # Extraire les niches de la réponse
        if "niches" in response:
            niches = response["niches"]
            
            # Enrichir les niches avec des métadonnées
            for niche in niches:
                niche["generated_at"] = datetime.utcnow().isoformat()
                niche["status"] = "pending"  # Status initial
            
            return niches
        else:
            self.logger.error("Format de réponse LLM invalide")
            return []
    
    def store_feedback(self, niche_id, feedback):
        """
        Stocke le feedback sur une niche générée.
        
        Args:
            niche_id: ID de la niche
            feedback: Données de feedback
            
        Returns:
            bool: Succès de l'opération
        """
        try:
            # Récupérer la niche
            niche = self.db.query(NicheModel).filter(NicheModel.id == niche_id).first()
            
            if not niche:
                self.logger.error(f"Niche avec ID {niche_id} non trouvée")
                return False
            
            # Mettre à jour avec le feedback
            niche.feedback_score = feedback.get('score')
            niche.feedback_text = feedback.get('text')
            niche.feedback_timestamp = datetime.utcnow()
            
            # Si la niche est rejetée, mettre à jour son statut
            if feedback.get('rejected', False):
                niche.status = "rejected"
                # Ajouter à la liste des niches rejetées pour référence future
                self.rejected_niches.append({
                    'name': niche.name,
                    'reason': feedback.get('text', 'Non spécifié')
                })
            else:
                niche.status = "approved"
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors du stockage du feedback: {str(e)}")
            return False
