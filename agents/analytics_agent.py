from datetime import datetime, timedelta
import time
import json
from typing import Dict, Any, List, Optional, Union
import logging
import pandas as pd
import numpy as np

from .base import BaseAgent
from .utils.llm import ask_llm, generate_structured_response

class AnalyticsAgent(BaseAgent):
    """
    Agent responsable de l'analyse des performances des campagnes.
    
    Cet agent génère des analyses détaillées, des rapports et des recommandations
    basées sur les métriques des campagnes.
    """
    
    def __init__(self, agent_id, db_session):
        super().__init__(agent_id, db_session)
    
    def run(self, input_data):
        """
        Exécute l'agent d'analyse.
        
        Args:
            input_data (dict): Les données d'entrée, qui peuvent inclure:
                - campaign_id: ID de la campagne à analyser
                - date_range: Plage de dates pour l'analyse
                - metrics: Liste des métriques à analyser
                - comparison: Comparaison avec d'autres périodes
                - format: Format de sortie (json, html, etc.)
                
        Returns:
            dict: Résultats de l'analyse
        """
        self.logger.info(f"Lancement de AnalyticsAgent avec données: {input_data}")
        
        start_time = time.time()
        
        try:
            # Extraire les paramètres
            campaign_id = input_data.get('campaign_id')
            date_range = input_data.get('date_range', {})
            metrics = input_data.get('metrics', ['all'])
            comparison = input_data.get('comparison', False)
            output_format = input_data.get('format', 'json')
            
            if not campaign_id:
                raise ValueError("campaign_id est requis")
            
            # Récupérer les données de la campagne
            campaign_data = self._get_campaign_data(campaign_id, date_range)
            
            # Analyser les données
            analysis_results = self._analyze_campaign_data(
                campaign_data=campaign_data,
                metrics=metrics,
                comparison=comparison
            )
            
            # Générer des recommandations
            recommendations = self._generate_recommendations(analysis_results)
            
            # Formater les résultats selon le format demandé
            formatted_results = self._format_results(
                analysis_results=analysis_results,
                recommendations=recommendations,
                output_format=output_format
            )
            
            # Stocker les résultats de l'analyse
            self._store_analysis_results(campaign_id, analysis_results, recommendations)
            
            execution_time = time.time() - start_time
            
            # Préparer les résultats complets
            results = {
                'campaign_id': campaign_id,
                'timestamp': datetime.utcnow().isoformat(),
                'analysis': formatted_results,
                'recommendations': recommendations,
                'execution_time': execution_time
            }
            
            # Logging des résultats
            self.log_execution(
                operation="analyze_campaign",
                input_data=input_data,
                output_data=results,
                status="success",
                execution_time=execution_time
            )
            
            return results
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Erreur lors de l'exécution de AnalyticsAgent: {str(e)}")
            
            # Logging de l'erreur
            self.log_execution(
                operation="analyze_campaign",
                input_data=input_data,
                output_data={"error": str(e)},
                status="error",
                execution_time=execution_time
            )
            
            return {"error": str(e)}
    
    def _get_campaign_data(self, campaign_id, date_range=None):
        """
        Récupère les données d'une campagne pour analyse.
        
        Args:
            campaign_id: ID de la campagne
            date_range: Plage de dates optionnelle
            
        Returns:
            dict: Données de la campagne avec métriques
        """
        try:
            # Récupérer la campagne
            campaign = self.db.query(CampaignModel).filter(CampaignModel.id == campaign_id).first()
            
            if not campaign:
                raise ValueError(f"Campagne avec ID {campaign_id} non trouvée")
            
            # Préparer les filtres de date
            start_date = None
            end_date = None
            
            if date_range:
                start_date = date_range.get('start')
                end_date = date_range.get('end')
            
            # Si aucune date n'est spécifiée, utiliser les 30 derniers jours
            if not start_date:
                end_date = datetime.utcnow()
                start_date = end_date - timedelta(days=30)
            
            # Récupérer les métriques
            metrics_query = """
                SELECT * FROM campaign_metrics
                WHERE campaign_id = :campaign_id
                AND timestamp BETWEEN :start_date AND :end_date
                ORDER BY timestamp ASC
            """
            
            metrics_result = self.db.execute(
                metrics_query, 
                {
                    "campaign_id": campaign_id,
                    "start_date": start_date,
                    "end_date": end_date
                }
            )
            
            metrics = [dict(row) for row in metrics_result]
            
            # Récupérer les leads associés
            leads_query = """
                SELECT l.*, ls.status as lead_status
                FROM leads l
                JOIN lead_status ls ON l.id = ls.lead_id
                WHERE l.campaign_id = :campaign_id
                AND l.created_at BETWEEN :start_date AND :end_date
            """
            
            leads_result = self.db.execute(
                leads_query,
                {
                    "campaign_id": campaign_id,
                    "start_date": start_date,
                    "end_date": end_date
                }
            )
            
            leads = [dict(row) for row in leads_result]
            
            # Assembler les données complètes
            campaign_data = {
                'campaign': {
                    'id': campaign.id,
                    'name': campaign.name,
                    'description': campaign.description,
                    'start_date': campaign.start_date.isoformat(),
                    'end_date': campaign.end_date.isoformat() if campaign.end_date else None,
                    'status': campaign.status,
                    'budget': campaign.budget,
                    'target_audience': campaign.target_audience,
                    'goals': campaign.goals
                },
                'metrics': metrics,
                'leads': leads,
                'date_range': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                }
            }
            
            return campaign_data
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des données de campagne: {str(e)}")
            raise
    
    def _analyze_campaign_data(self, campaign_data, metrics=None, comparison=False):
        """
        Analyse les données de la campagne.
        
        Args:
            campaign_data: Données de la campagne à analyser
            metrics: Liste des métriques spécifiques à analyser
            comparison: Indique si une comparaison doit être effectuée
            
        Returns:
            dict: Résultats de l'analyse
        """
        try:
            # Vérifier si metrics contient 'all'
            analyze_all = 'all' in metrics
            
            # Initialiser les résultats
            results = {
                'summary': {},
                'detailed': {},
                'trends': {},
            }
            
            # Convertir les métriques en DataFrame pour faciliter l'analyse
            metrics_df = pd.DataFrame(campaign_data['metrics'])
            
            # Si le DataFrame est vide, retourner des résultats vides
            if metrics_df.empty:
                return results
            
            # Convertir timestamp en datetime
            metrics_df['timestamp'] = pd.to_datetime(metrics_df['timestamp'])
            
            # Métriques principales à analyser
            main_metrics = [
                'impressions', 'clicks', 'conversions', 'cost',
                'revenue', 'leads_generated', 'messages_sent'
            ]
            
            # Filtrer les métriques à analyser
            if not analyze_all:
                main_metrics = [m for m in main_metrics if m in metrics]
            
            # Analyse sommaire
            summary = {}
            for metric in main_metrics:
                if metric in metrics_df.columns:
                    summary[metric] = {
                        'total': metrics_df[metric].sum(),
                        'average': metrics_df[metric].mean(),
                        'min': metrics_df[metric].min(),
                        'max': metrics_df[metric].max()
                    }
            
            # Calcul des KPIs dérivés
            if 'clicks' in metrics_df.columns and 'impressions' in metrics_df.columns:
                click_through_rate = metrics_df['clicks'].sum() / metrics_df['impressions'].sum() if metrics_df['impressions'].sum() > 0 else 0
                summary['ctr'] = {
                    'value': click_through_rate,
                    'formatted': f"{click_through_rate * 100:.2f}%"
                }
            
            if 'conversions' in metrics_df.columns and 'clicks' in metrics_df.columns:
                conversion_rate = metrics_df['conversions'].sum() / metrics_df['clicks'].sum() if metrics_df['clicks'].sum() > 0 else 0
                summary['conversion_rate'] = {
                    'value': conversion_rate,
                    'formatted': f"{conversion_rate * 100:.2f}%"
                }
            
            if 'revenue' in metrics_df.columns and 'cost' in metrics_df.columns:
                roi = (metrics_df['revenue'].sum() - metrics_df['cost'].sum()) / metrics_df['cost'].sum() if metrics_df['cost'].sum() > 0 else 0
                summary['roi'] = {
                    'value': roi,
                    'formatted': f"{roi * 100:.2f}%"
                }
            
            results['summary'] = summary
            
            # Analyse détaillée par période (jour, semaine, mois)
            if not metrics_df.empty:
                # Grouper par jour
                daily_metrics = metrics_df.groupby(metrics_df['timestamp'].dt.date).sum()
                results['detailed']['daily'] = daily_metrics.to_dict(orient='index')
                
                # Grouper par semaine
                weekly_metrics = metrics_df.groupby(pd.Grouper(key='timestamp', freq='W')).sum()
                results['detailed']['weekly'] = {str(date): values for date, values in weekly_metrics.to_dict(orient='index').items()}
                
                # Grouper par mois
                monthly_metrics = metrics_df.groupby(pd.Grouper(key='timestamp', freq='M')).sum()
                results['detailed']['monthly'] = {str(date): values for date, values in monthly_metrics.to_dict(orient='index').items()}
            
            # Analyse des tendances
            if len(metrics_df) > 1:
                for metric in main_metrics:
                    if metric in metrics_df.columns:
                        # Calculer la tendance (augmentation/diminution)
                        first_value = metrics_df[metric].iloc[0]
                        last_value = metrics_df[metric].iloc[-1]
                        
                        if first_value > 0:
                            change_pct = (last_value - first_value) / first_value
                        else:
                            change_pct = float('inf') if last_value > 0 else 0
                        
                        # Déterminer la direction de la tendance
                        trend_direction = "stable"
                        if change_pct > 0.05:  # +5%
                            trend_direction = "increasing"
                        elif change_pct < -0.05:  # -5%
                            trend_direction = "decreasing"
                        
                        results['trends'][metric] = {
                            'direction': trend_direction,
                            'change_percent': change_pct,
                            'formatted': f"{change_pct * 100:.1f}%"
                        }
            
            # Ajouter des analyses sur les leads si disponibles
            if 'leads' in campaign_data and campaign_data['leads']:
                leads_df = pd.DataFrame(campaign_data['leads'])
                
                # Analyse des statuts des leads
                if 'lead_status' in leads_df.columns:
                    status_counts = leads_df['lead_status'].value_counts().to_dict()
                    total_leads = len(leads_df)
                    
                    results['leads'] = {
                        'total': total_leads,
                        'status_distribution': {
                            status: {
                                'count': count,
                                'percentage': f"{(count / total_leads) * 100:.1f}%"
                            }
                            for status, count in status_counts.items()
                        }
                    }
            
            # Comparaison avec période précédente si demandé
            if comparison:
                # Déterminer la durée de la période analysée
                start_date = pd.to_datetime(campaign_data['date_range']['start'])
                end_date = pd.to_datetime(campaign_data['date_range']['end'])
                period_duration = (end_date - start_date).days
                
                # Définir la période précédente
                prev_end_date = start_date - timedelta(days=1)
                prev_start_date = prev_end_date - timedelta(days=period_duration)
                
                # Récupérer les données de la période précédente
                prev_date_range = {
                    'start': prev_start_date.isoformat(),
                    'end': prev_end_date.isoformat()
                }
                
                try:
                    prev_campaign_data = self._get_campaign_data(
                        campaign_id=campaign_data['campaign']['id'],
                        date_range=prev_date_range
                    )
                    
                    prev_metrics_df = pd.DataFrame(prev_campaign_data['metrics'])
                    
                    # Si nous avons des données pour la période précédente
                    if not prev_metrics_df.empty:
                        comparison_results = {}
                        
                        for metric in main_metrics:
                            if metric in metrics_df.columns and metric in prev_metrics_df.columns:
                                current_total = metrics_df[metric].sum()
                                prev_total = prev_metrics_df[metric].sum()
                                
                                if prev_total > 0:
                                    change_pct = (current_total - prev_total) / prev_total
                                else:
                                    change_pct = float('inf') if current_total > 0 else 0
                                
                                comparison_results[metric] = {
                                    'current_period': current_total,
                                    'previous_period': prev_total,
                                    'change': current_total - prev_total,
                                    'change_percent': change_pct,
                                    'formatted': f"{change_pct * 100:.1f}%"
                                }
                        
                        results['comparison'] = comparison_results
                        
                except Exception as e:
                    self.logger.warning(f"Impossible de générer une comparaison: {str(e)}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'analyse des données: {str(e)}")
            return {'error': str(e)}
    
    def _generate_recommendations(self, analysis_results):
        """
        Génère des recommandations basées sur les résultats d'analyse.
        
        Args:
            analysis_results: Résultats de l'analyse
            
        Returns:
            list: Liste de recommandations
        """
        # Schéma pour les recommandations
        recommendation_schema = {
            "recommendations": [
                {
                    "title": "Titre de la recommandation",
                    "description": "Description détaillée",
                    "impact": "Impact attendu (high/medium/low)",
                    "action_items": ["Action 1", "Action 2"]
                }
            ]
        }
        
        # Convertir les résultats d'analyse en format JSON
        analysis_json = json.dumps(analysis_results, default=str)
        
        # Construire le prompt
        prompt = f"""
        En tant qu'expert en analyse de campagnes marketing, génère des recommandations
        stratégiques basées sur ces résultats d'analyse:
        
        {analysis_json}
        
        Fournis entre 3 et 5 recommandations concrètes, exploitables et pertinentes.
        Pour chaque recommandation, inclus:
        1. Un titre clair et concis
        2. Une description détaillée de la recommandation
        3. Une évaluation de l'impact attendu (high/medium/low)
        4. 2-3 actions concrètes pour mettre en œuvre la recommandation
        
        Base tes recommandations sur les tendances, écarts de performance, et opportunités
        identifiées dans les données d'analyse.
        """
        
        # Générer les recommandations via LLM
        response = generate_structured_response(
            prompt=prompt,
            schema=recommendation_schema,
            system_message="Tu es un expert en analyse marketing qui formule des recommandations stratégiques pertinentes, exploitables et basées sur des données.",
            model="gpt-4.1",
            complexity="standard"  # Analyse complexe nécessitant le modèle standard
        )
        
        # Extraire les recommandations
        if "recommendations" in response:
            recommendations = response["recommendations"]
            
            # Ajouter un timestamp à chaque recommandation
            for rec in recommendations:
                rec["generated_at"] = datetime.utcnow().isoformat()
            
            return recommendations
        else:
            self.logger.error("Format de réponse LLM invalide pour les recommandations")
            return []
    
    def _format_results(self, analysis_results, recommendations, output_format='json'):
        """
        Formate les résultats selon le format demandé.
        
        Args:
            analysis_results: Résultats de l'analyse
            recommendations: Recommandations générées
            output_format: Format de sortie (json, html, etc.)
            
        Returns:
            str or dict: Résultats formatés
        """
        if output_format == 'json':
            # Déjà en format dict, simplement combiner
            return {
                'analysis': analysis_results,
                'recommendations': recommendations
            }
        
        elif output_format == 'html':
            # Génération d'un rapport HTML simple
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Rapport d'analyse de campagne</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    h1, h2, h3 {{ color: #333; }}
                    .card {{ border: 1px solid #ddd; border-radius: 4px; padding: 15px; margin-bottom: 20px; }}
                    .metric {{ display: inline-block; margin-right: 20px; margin-bottom: 10px; }}
                    .metric-value {{ font-size: 24px; font-weight: bold; }}
                    .metric-label {{ font-size: 14px; color: #666; }}
                    .trend-up {{ color: green; }}
                    .trend-down {{ color: red; }}
                    .trend-stable {{ color: orange; }}
                    table {{ border-collapse: collapse; width: 100%; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                </style>
            </head>
            <body>
                <h1>Rapport d'analyse de campagne</h1>
                <p>Généré le {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}</p>
                
                <div class="card">
                    <h2>Résumé</h2>
                    <div>
            """
            
            # Ajouter les métriques du résumé
            for metric, values in analysis_results.get('summary', {}).items():
                if isinstance(values, dict) and 'total' in values:
                    html_content += f"""
                    <div class="metric">
                        <div class="metric-value">{values['total']}</div>
                        <div class="metric-label">{metric.replace('_', ' ').title()}</div>
                    </div>
                    """
                elif isinstance(values, dict) and 'value' in values:
                    html_content += f"""
                    <div class="metric">
                        <div class="metric-value">{values['formatted']}</div>
                        <div class="metric-label">{metric.replace('_', ' ').title()}</div>
                    </div>
                    """
            
            html_content += """
                    </div>
                </div>
                
                <div class="card">
                    <h2>Tendances</h2>
                    <table>
                        <tr>
                            <th>Métrique</th>
                            <th>Direction</th>
                            <th>Changement</th>
                        </tr>
            """
            
            # Ajouter les tendances
            for metric, trend in analysis_results.get('trends', {}).items():
                direction = trend.get('direction', 'stable')
                css_class = f"trend-{direction}"
                html_content += f"""
                <tr>
                    <td>{metric.replace('_', ' ').title()}</td>
                    <td class="{css_class}">{direction.title()}</td>
                    <td>{trend.get('formatted', '0%')}</td>
                </tr>
                """
            
            html_content += """
                    </table>
                </div>
                
                <div class="card">
                    <h2>Recommandations</h2>
            """
            
            # Ajouter les recommandations
            for i, rec in enumerate(recommendations):
                html_content += f"""
                <div>
                    <h3>{i+1}. {rec.get('title', 'Recommandation')}</h3>
                    <p>{rec.get('description', '')}</p>
                    <p><strong>Impact:</strong> {rec.get('impact', 'Medium')}</p>
                    <ul>
                """
                
                for action in rec.get('action_items', []):
                    html_content += f"<li>{action}</li>"
                
                html_content += """
                    </ul>
                </div>
                """
            
            html_content += """
                </div>
            </body>
            </html>
            """
            
            return html_content
        
        else:
            # Format par défaut
            return {
                'analysis': analysis_results,
                'recommendations': recommendations
            }
    
    def _store_analysis_results(self, campaign_id, analysis_results, recommendations):
        """
        Stocke les résultats de l'analyse dans la base de données.
        
        Args:
            campaign_id: ID de la campagne
            analysis_results: Résultats de l'analyse
            recommendations: Recommandations générées
        """
        try:
            # Préparer les données à stocker
            analysis_data = {
                'campaign_id': campaign_id,
                'analysis_data': json.dumps(analysis_results, default=str),
                'recommendations': json.dumps(recommendations, default=str),
                'created_at': datetime.utcnow()
            }
            
            # Créer une nouvelle entrée d'analyse
            new_analysis = CampaignAnalysisModel(**analysis_data)
            self.db.add(new_analysis)
            self.db.commit()
            
            self.logger.info(f"Analyse stockée avec succès pour la campagne {campaign_id}")
            
        except Exception as e:
            self.logger.error(f"Erreur lors du stockage de l'analyse: {str(e)}")
            self.db.rollback()
    
    def export_analysis(self, analysis_id, format='json'):
        """
        Exporte une analyse dans le format spécifié.
        
        Args:
            analysis_id: ID de l'analyse à exporter
            format: Format d'exportation
            
        Returns:
            dict or str: Données exportées
        """
        try:
            # Récupérer l'analyse
            analysis = self.db.query(CampaignAnalysisModel).filter(
                CampaignAnalysisModel.id == analysis_id
            ).first()
            
            if not analysis:
                raise ValueError(f"Analyse avec ID {analysis_id} non trouvée")
            
            # Charger les données JSON
            analysis_data = json.loads(analysis.analysis_data)
            recommendations = json.loads(analysis.recommendations)
            
            # Formater selon le format demandé
            return self._format_results(
                analysis_results=analysis_data,
                recommendations=recommendations,
                output_format=format
            )
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'exportation de l'analyse: {str(e)}")
            return {"error": str(e)}
    
    def store_feedback(self, analysis_id, feedback):
        """
        Stocke le feedback sur une analyse.
        
        Args:
            analysis_id: ID de l'analyse
            feedback: Données de feedback
            
        Returns:
            bool: Succès de l'opération
        """
        try:
            # Récupérer l'analyse
            analysis = self.db.query(CampaignAnalysisModel).filter(
                CampaignAnalysisModel.id == analysis_id
            ).first()
            
            if not analysis:
                self.logger.error(f"Analyse avec ID {analysis_id} non trouvée")
                return False
            
            # Mettre à jour avec le feedback
            analysis.feedback_score = feedback.get('score')
            analysis.feedback_text = feedback.get('text')
            analysis.feedback_timestamp = datetime.utcnow()
            
            self.db.commit()
            
            # Log le feedback
            self.logger.info(f"Feedback enregistré pour l'analyse {analysis_id}: Score {feedback.get('score')}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors du stockage du feedback: {str(e)}")
            self.db.rollback()
            return False
