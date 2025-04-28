from datetime import datetime
import time
import json
from typing import Dict, Any, List, Optional
import logging

from .base import BaseAgent
from .utils.llm import ask_llm, generate_structured_response

class PivotAgent(BaseAgent):
    """
    Agent responsable de l'analyse et de la décision de pivot stratégique.
    
    Cet agent analyse les performances des campagnes et recommande
    des ajustements stratégiques ou des pivots complets si nécessaire.
    """
    
    def __init__(self, agent_id, db_session):
        super().__init__(agent_id, db_session)
    
    def run(self, input_data):
        """
        Exécute l'agent de pivot.
        
        Args:
            input_data (dict): Les données d'entrée, qui peuvent inclure:
                - campaign_id: ID de la campagne à analyser
                - metrics: Métriques de performance
                - thresholds: Seuils d'alerte pour les métriques
                - historical_data: Données historiques de la campagne
                
        Returns:
            dict: Résultats de l'évaluation et recommandations de pivot
        """
        self.logger.info(f"Lancement de PivotAgent avec données: {input_data}")
        
        start_time = time.time()
        
        try:
            # Extraire les paramètres
            campaign_id = input_data.get('campaign_id')
            metrics = input_data.get('metrics', {})
            thresholds = input_data.get('thresholds', {})
            historical_data = input_data.get('historical_data', [])
            
            if not campaign_id:
                raise ValueError("campaign_id est requis")
            
            # Récupérer les données de la campagne si non fournies
            if not metrics or not historical_data:
                campaign_data = self._get_campaign_data(campaign_id)
                metrics = campaign_data.get('current_metrics', {})
                historical_data = campaign_data.get('historical_data', [])
            
            # Évaluer les performances actuelles
            performance_evaluation = self._evaluate_performance(
                metrics=metrics,
                thresholds=thresholds
            )
            
            # Analyser les tendances
            trend_analysis = self._analyze_trends(historical_data)
            
            # Déterminer si un pivot est nécessaire
            pivot_decision = self._make_pivot_decision(
                performance_evaluation=performance_evaluation,
                trend_analysis=trend_analysis
            )
            
            # Générer des recommandations de pivot si nécessaire
            pivot_recommendations = {}
            if pivot_decision['pivot_recommended']:
                pivot_recommendations = self._generate_pivot_recommendations(
                    campaign_id=campaign_id,
                    performance_evaluation=performance_evaluation,
                    trend_analysis=trend_analysis
                )
            
            execution_time = time.time() - start_time
            
            # Préparer les résultats complets
            results = {
                'campaign_id': campaign_id,
                'timestamp': datetime.utcnow().isoformat(),
                'performance_evaluation': performance_evaluation,
                'trend_analysis': trend_analysis,
                'pivot_decision': pivot_decision,
                'pivot_recommendations': pivot_recommendations,
                'execution_time': execution_time
            }
            
            # Logging des résultats
            self.log_execution(
                operation="evaluate_pivot",
                input_data=input_data,
                output_data=results,
                status="success",
                execution_time=execution_time
            )
            
            return results
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Erreur lors de l'exécution de PivotAgent: {str(e)}")
            
            # Logging de l'erreur
            self.log_execution(
                operation="evaluate_pivot",
                input_data=input_data,
                output_data={"error": str(e)},
                status="error",
                execution_time=execution_time
            )
            
            return {"error": str(e)}
    
    def _get_campaign_data(self, campaign_id):
        """
        Récupère les données actuelles et historiques d'une campagne.
        
        Args:
            campaign_id: ID de la campagne
            
        Returns:
            dict: Données de la campagne
        """
        try:
            # Récupérer la campagne
            campaign = self.db.query(CampaignModel).filter(CampaignModel.id == campaign_id).first()
            
            if not campaign:
                raise ValueError(f"Campagne avec ID {campaign_id} non trouvée")
            
            # Récupérer les métriques actuelles (dernière période)
            current_metrics_query = """
                SELECT * FROM campaign_metrics
                WHERE campaign_id = :campaign_id
                ORDER BY timestamp DESC
                LIMIT 1
            """
            
            current_metrics_result = self.db.execute(
                current_metrics_query, 
                {
                    "campaign_id": campaign_id
                }
            )
            
            current_metrics = [dict(row) for row in current_metrics_result]
            
            # Récupérer les données historiques
            historical_data_query = """
                SELECT * FROM campaign_metrics
                WHERE campaign_id = :campaign_id
                ORDER BY timestamp ASC
            """
            
            historical_data_result = self.db.execute(
                historical_data_query,
                {
                    "campaign_id": campaign_id
                }
            )
            
            historical_data = [dict(row) for row in historical_data_result]
            
            # Récupérer les données de leads
            leads_query = """
                SELECT COUNT(*) as lead_count, 
                       SUM(CASE WHEN ls.status = 'converted' THEN 1 ELSE 0 END) as conversions
                FROM leads l
                JOIN lead_status ls ON l.id = ls.lead_id
                WHERE l.campaign_id = :campaign_id
            """
            
            leads_result = self.db.execute(
                leads_query,
                {
                    "campaign_id": campaign_id
                }
            )
            
            leads_data = [dict(row) for row in leads_result]
            
            # Assembler les données
            campaign_data = {
                'campaign_info': {
                    'id': campaign.id,
                    'name': campaign.name,
                    'status': campaign.status,
                    'budget': campaign.budget,
                    'start_date': campaign.start_date.isoformat() if campaign.start_date else None,
                    'end_date': campaign.end_date.isoformat() if campaign.end_date else None,
                },
                'current_metrics': current_metrics[0] if current_metrics else {},
                'historical_data': historical_data,
                'leads_data': leads_data[0] if leads_data else {}
            }
            
            return campaign_data
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des données de campagne: {str(e)}")
            raise
    
    def _evaluate_performance(self, metrics, thresholds):
        """
        Évalue les performances actuelles par rapport aux seuils.
        
        Args:
            metrics (dict): Métriques actuelles
            thresholds (dict): Seuils d'alerte
            
        Returns:
            dict: Évaluation des performances
        """
        evaluation = {
            'metrics_evaluation': {},
            'overall_status': 'good',
            'problem_areas': [],
            'score': 0.0
        }
        
        # Définir des seuils par défaut si non fournis
        default_thresholds = {
            'roi': {'warning': 0.5, 'critical': 0.0},
            'ctr': {'warning': 0.01, 'critical': 0.005},
            'conversion_rate': {'warning': 0.02, 'critical': 0.01},
            'cost_per_acquisition': {'warning': 50.0, 'critical': 100.0},
            'leads_generated': {'warning': 10, 'critical': 5}
        }
        
        # Fusionner avec les seuils fournis
        for key, value in default_thresholds.items():
            if key not in thresholds:
                thresholds[key] = value
        
        # Évaluer chaque métrique disponible
        total_metrics = 0
        total_score = 0.0
        
        for metric_name, metric_value in metrics.items():
            # Ignorer les champs non numériques
            if not isinstance(metric_value, (int, float)):
                continue
                
            # Vérifier si nous avons des seuils pour cette métrique
            if metric_name in thresholds:
                threshold = thresholds[metric_name]
                
                metric_status = 'good'
                metric_score = 1.0
                
                # Vérifier les seuils (logique inversée pour certaines métriques)
                if metric_name in ['cost_per_acquisition', 'cost']:
                    # Pour ces métriques, plus bas est mieux
                    if metric_value > threshold.get('critical', float('inf')):
                        metric_status = 'critical'
                        metric_score = 0.0
                    elif metric_value > threshold.get('warning', float('inf')):
                        metric_status = 'warning'
                        metric_score = 0.5
                else:
                    # Pour les autres métriques, plus haut est mieux
                    if metric_value < threshold.get('critical', 0):
                        metric_status = 'critical'
                        metric_score = 0.0
                    elif metric_value < threshold.get('warning', 0):
                        metric_status = 'warning'
                        metric_score = 0.5
                
                # Ajouter à l'évaluation
                evaluation['metrics_evaluation'][metric_name] = {
                    'value': metric_value,
                    'status': metric_status,
                    'score': metric_score,
                    'threshold_warning': threshold.get('warning'),
                    'threshold_critical': threshold.get('critical')
                }
                
                # Mettre à jour le statut global
                if metric_status == 'critical' and evaluation['overall_status'] != 'critical':
                    evaluation['overall_status'] = 'critical'
                    evaluation['problem_areas'].append(metric_name)
                elif metric_status == 'warning' and evaluation['overall_status'] == 'good':
                    evaluation['overall_status'] = 'warning'
                    evaluation['problem_areas'].append(metric_name)
                
                # Mettre à jour le score total
                total_metrics += 1
                total_score += metric_score
        
        # Calculer le score global
        if total_metrics > 0:
            evaluation['score'] = total_score / total_metrics
        
        return evaluation
    
    def _analyze_trends(self, historical_data):
        """
        Analyse les tendances basées sur les données historiques.
        
        Args:
            historical_data (list): Données historiques de la campagne
            
        Returns:
            dict: Analyse des tendances
        """
        if not historical_data:
            return {'error': 'Pas de données historiques disponibles'}
        
        trends = {
            'metrics_trends': {},
            'overall_trend': 'stable',
            'declining_metrics': [],
            'improving_metrics': []
        }
        
        # Métriques à analyser
        metrics_to_analyze = [
            'impressions', 'clicks', 'conversions', 'cost',
            'revenue', 'roi', 'ctr', 'conversion_rate', 'cost_per_acquisition'
        ]
        
        # Organiser les données par métrique
        metrics_data = {}
        timestamps = []
        
        for entry in historical_data:
            timestamp = entry.get('timestamp')
            timestamps.append(timestamp)
            
            for metric in metrics_to_analyze:
                if metric in entry:
                    if metric not in metrics_data:
                        metrics_data[metric] = []
                    metrics_data[metric].append(entry[metric])
        
        # Analyser chaque métrique
        for metric, values in metrics_data.items():
            if len(values) >= 2:
                # Calculer la tendance sur les 3 dernières périodes ou moins
                recent_values = values[-min(3, len(values)):]
                
                # Calculer le taux de variation
                first_value = recent_values[0]
                last_value = recent_values[-1]
                
                if first_value != 0:
                    change_rate = (last_value - first_value) / first_value
                else:
                    change_rate = 0.0 if last_value == 0 else float('inf')
                
                # Déterminer la direction de la tendance
                trend_direction = 'stable'
                if metric in ['cost', 'cost_per_acquisition']:
                    # Pour ces métriques, une baisse est positive
                    if change_rate < -0.1:
                        trend_direction = 'improving'
                    elif change_rate > 0.1:
                        trend_direction = 'declining'
                else:
                    # Pour les autres métriques, une hausse est positive
                    if change_rate > 0.1:
                        trend_direction = 'improving'
                    elif change_rate < -0.1:
                        trend_direction = 'declining'
                
                # Ajouter à l'analyse
                trends['metrics_trends'][metric] = {
                    'values': values,
                    'change_rate': change_rate,
                    'direction': trend_direction,
                    'formatted_change': f"{change_rate * 100:.1f}%"
                }
                
                # Mettre à jour les listes d'amélioration/déclin
                if trend_direction == 'declining':
                    trends['declining_metrics'].append(metric)
                elif trend_direction == 'improving':
                    trends['improving_metrics'].append(metric)
        
        # Déterminer la tendance globale
        if trends['declining_metrics'] and len(trends['declining_metrics']) > len(trends['improving_metrics']):
            trends['overall_trend'] = 'declining'
        elif trends['improving_metrics'] and len(trends['improving_metrics']) > len(trends['declining_metrics']):
            trends['overall_trend'] = 'improving'
        
        return trends
    
    def _make_pivot_decision(self, performance_evaluation, trend_analysis):
        """
        Détermine si un pivot est nécessaire.
        
        Args:
            performance_evaluation (dict): Évaluation des performances
            trend_analysis (dict): Analyse des tendances
            
        Returns:
            dict: Décision de pivot
        """
        decision = {
            'pivot_recommended': False,
            'confidence': 0.0,
            'reasons': [],
            'pivot_type': None
        }
        
        # Facteurs pour recommander un pivot
        pivot_factors = []
        
        # 1. Vérifier les performances actuelles
        if performance_evaluation['overall_status'] == 'critical':
            pivot_factors.append({
                'type': 'performance_critical',
                'weight': 0.8,
                'description': "Les performances sont critiques sur plusieurs métriques clés"
            })
        elif performance_evaluation['overall_status'] == 'warning':
            pivot_factors.append({
                'type': 'performance_warning',
                'weight': 0.5,
                'description': "Plusieurs métriques sont sous les seuils d'alerte"
            })
        
        # 2. Vérifier les tendances
        if trend_analysis['overall_trend'] == 'declining':
            pivot_factors.append({
                'type': 'trend_declining',
                'weight': 0.7,
                'description': "Les tendances sont négatives sur plusieurs métriques clés"
            })
        
        # 3. Vérifier spécifiquement le ROI et le taux de conversion
        if 'roi' in performance_evaluation['metrics_evaluation']:
            roi_eval = performance_evaluation['metrics_evaluation']['roi']
            if roi_eval['status'] == 'critical':
                pivot_factors.append({
                    'type': 'roi_critical',
                    'weight': 0.9,
                    'description': "ROI critique, la campagne n'est pas rentable"
                })
        
        if 'conversion_rate' in performance_evaluation['metrics_evaluation']:
            conv_eval = performance_evaluation['metrics_evaluation']['conversion_rate']
            if conv_eval['status'] == 'critical':
                pivot_factors.append({
                    'type': 'conversion_critical',
                    'weight': 0.8,
                    'description': "Taux de conversion critique, problème dans le funnel de conversion"
                })
        
        # Calculer le score de confiance pour un pivot
        total_weight = 0.0
        confidence_score = 0.0
        
        for factor in pivot_factors:
            total_weight += factor['weight']
            confidence_score += factor['weight']
        
        if total_weight > 0:
            confidence_score = confidence_score / total_weight
        
        # Déterminer si un pivot est recommandé
        if confidence_score >= 0.7:
            decision['pivot_recommended'] = True
            decision['confidence'] = confidence_score
            decision['reasons'] = [factor['description'] for factor in pivot_factors]
            
            # Déterminer le type de pivot
            if confidence_score >= 0.9:
                decision['pivot_type'] = 'major'  # Pivot majeur (changement complet de stratégie)
            elif confidence_score >= 0.8:
                decision['pivot_type'] = 'moderate'  # Pivot modéré (ajustements significatifs)
            else:
                decision['pivot_type'] = 'minor'  # Pivot mineur (ajustements tactiques)
        
        return decision
    
    def _generate_pivot_recommendations(self, campaign_id, performance_evaluation, trend_analysis):
        """
        Génère des recommandations de pivot.
        
        Args:
            campaign_id: ID de la campagne
            performance_evaluation: Évaluation des performances
            trend_analysis: Analyse des tendances
            
        Returns:
            dict: Recommandations de pivot
        """
        # Récupérer les informations supplémentaires sur la campagne
        campaign = self.db.query(CampaignModel).filter(CampaignModel.id == campaign_id).first()
        
        if not campaign:
            return {'error': 'Campagne non trouvée'}
        
        # Schéma pour les recommandations
        recommendation_schema = {
            "pivot_strategy": {
                "title": "Titre de la stratégie de pivot",
                "description": "Description détaillée de la stratégie",
                "pivot_type": "Type de pivot (major/moderate/minor)",
                "risk_level": "Niveau de risque (high/medium/low)",
                "expected_outcome": "Résultat attendu"
            },
            "tactical_recommendations": [
                {
                    "area": "Domaine d'action",
                    "description": "Description de l'action",
                    "priority": "Priorité (high/medium/low)",
                    "steps": ["Étape 1", "Étape 2"]
                }
            ]
        }
        
        # Convertir les données en JSON pour le prompt
        data_json = json.dumps(
            {
                'campaign': {
                    'id': campaign.id,
                    'name': campaign.name,
                    'niche': campaign.niche,
                    'target_audience': campaign.target_audience,
                    'goals': campaign.goals,
                    'budget': campaign.budget,
                    'current_strategy': campaign.strategy
                },
                'performance': performance_evaluation,
                'trends': trend_analysis
            },
            default=str
        )
        
        # Construire le prompt
        prompt = f"""
        En tant qu'expert en stratégie marketing, tu dois formuler une stratégie de pivot
        pour une campagne qui montre des signes de sous-performance.
        
        Données de la campagne et analyses:
        {data_json}
        
        Basé sur ces données, propose:
        
        1. Une stratégie globale de pivot avec:
           - Un titre clair
           - Une description détaillée de la stratégie
           - Le type de pivot requis (major/moderate/minor)
           - Le niveau de risque associé
           - Les résultats attendus
        
        2. Entre 3 et 5 recommandations tactiques incluant pour chacune:
           - Le domaine concerné (audience, message, canal, offre, etc.)
           - Une description précise de l'action à entreprendre
           - Une priorité d'implémentation
           - Les étapes concrètes pour mettre en œuvre cette action
        
        Assure-toi que tes recommandations sont:
        - Directement liées aux problèmes identifiés
        - Précises et actionnables
        - Cohérentes avec le type de pivot recommandé
        - Adaptées au contexte spécifique de la campagne
        """
        
        # Générer les recommandations via LLM
        response = generate_structured_response(
            prompt=prompt,
            schema=recommendation_schema,
            system_message="Tu es un expert en stratégie marketing spécialisé dans le pivotement de campagnes sous-performantes.",
            model="gpt-4.1"
        )
        
        # Ajouter un timestamp
        response['generated_at'] = datetime.utcnow().isoformat()
        
        return response
    
    def store_feedback(self, pivot_id, feedback):
        """
        Stocke le feedback sur une décision de pivot.
        
        Args:
            pivot_id: ID de la décision de pivot
            feedback: Données de feedback
            
        Returns:
            bool: Succès de l'opération
        """
        try:
            # Récupérer la décision de pivot
            pivot_decision = self.db.query(PivotDecisionModel).filter(
                PivotDecisionModel.id == pivot_id
            ).first()
            
            if not pivot_decision:
                self.logger.error(f"Décision de pivot avec ID {pivot_id} non trouvée")
                return False
            
            # Mettre à jour avec le feedback
            pivot_decision.feedback_score = feedback.get('score')
            pivot_decision.feedback_text = feedback.get('text')
            pivot_decision.feedback_timestamp = datetime.utcnow()
            
            # Si le feedback inclut un statut d'implémentation
            if 'implementation_status' in feedback:
                pivot_decision.implementation_status = feedback['implementation_status']
            
            # Si le feedback inclut des résultats d'implémentation
            if 'implementation_results' in feedback:
                pivot_decision.implementation_results = feedback['implementation_results']
            
            self.db.commit()
            
            # Log le feedback
            self.logger.info(f"Feedback enregistré pour la décision de pivot {pivot_id}: Score {feedback.get('score')}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors du stockage du feedback: {str(e)}")
            self.db.rollback()
            return False
