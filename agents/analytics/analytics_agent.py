from agents.base.base import AgentBase
from utils.llm import ask_gpt_4_1
from logs.agent_logger import log_agent
from agents.analytics.campaign_analytics import CampaignAnalytics
import json
import datetime
import os
# Commenting out visualization imports as we're not generating actual plots in our test
# import matplotlib.pyplot as plt
# import io
# import base64

class AnalyticsAgent(AgentBase):
    def __init__(self):
        super().__init__("AnalyticsAgent")
        self.prompt_path = "prompts/analytics_agent_prompt.txt"
        self.analytics_engine = CampaignAnalytics()
        self.reports_dir = "logs/analytics_reports"
        self.verbosity = False  # Mode verbeux désactivé par défaut
        self._ensure_directories_exist()
    
    def _ensure_directories_exist(self):
        """Ensures that necessary directories for analytics exist"""
        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir, exist_ok=True)
    
    def run(self, input_data: dict) -> dict:
        print(f"[{self.name}] 📊 Analyse des données en cours...")
        
        # Extraire les paramètres d'entrée
        operation = input_data.get("operation", "analyze_campaign")
        campaign_id = input_data.get("campaign_id", None)
        niche = input_data.get("niche", None)
        time_period = input_data.get("time_period", "all")
        output_format = input_data.get("output_format", "json")
        verbose = input_data.get("verbose", False)
        
        # Activer le mode verbeux si demandé
        self.verbosity = verbose
        
        # Valider les paramètres requis
        if not campaign_id and not niche:
            result = {
                "error": "Paramètre requis manquant: campaign_id ou niche",
                "operation": operation,
                "status": "FAILED"
            }
            log_agent(self.name, input_data, result)
            return result
        
        # Préparer le résultat
        result = {
            "operation": operation,
            "campaign_id": campaign_id,
            "niche": niche,
            "time_period": time_period,
            "status": "PROCESSING",
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        # Obtenir les données d'analyse
        try:
            if campaign_id:
                campaign_data = self.analytics_engine.get_campaign_data(campaign_id)
            elif niche:
                campaign_data = self.analytics_engine.get_niche_data(niche)
            else:
                campaign_data = {}
            
            # Filtrer par période si nécessaire
            if time_period != "all":
                campaign_data = self.analytics_engine.filter_by_time_period(campaign_data, time_period)
            
            # Vérifier que des données existent
            if not campaign_data:
                result = {
                    "error": f"Aucune donnée trouvée pour {'campaign_id: ' + campaign_id if campaign_id else 'niche: ' + niche}",
                    "operation": operation,
                    "status": "COMPLETED",
                    "data": {}
                }
                log_agent(self.name, input_data, result)
                return result
            
            # Charger le prompt
            try:
                with open(self.prompt_path, "r") as file:
                    prompt_template = file.read()
            except Exception as e:
                result = {
                    "error": f"Erreur lors du chargement du prompt: {str(e)}",
                    "operation": operation,
                    "status": "FAILED"
                }
                log_agent(self.name, input_data, result)
                return result
            
            # Exécuter l'opération demandée
            if operation == "analyze_campaign":
                result = self._analyze_campaign(prompt_template, campaign_data, output_format, result)
            elif operation == "identify_levers":
                result = self._identify_performance_levers(prompt_template, campaign_data, output_format, result)
            elif operation == "compare_campaigns":
                comparison_id = input_data.get("comparison_id")
                if not comparison_id:
                    result["error"] = "Paramètre comparison_id requis pour la comparaison de campagnes"
                    result["status"] = "FAILED"
                else:
                    comparison_data = self.analytics_engine.get_campaign_data(comparison_id)
                    result = self._compare_campaigns(prompt_template, campaign_data, comparison_data, output_format, result)
            elif operation == "predict_performance":
                result = self._predict_performance(prompt_template, campaign_data, output_format, result)
            else:
                result["error"] = f"Opération non reconnue: {operation}"
                result["status"] = "FAILED"
        
        except Exception as e:
            result = {
                "error": f"Erreur lors de l'analyse: {str(e)}",
                "operation": operation,
                "status": "FAILED"
            }
        
        # Enregistrer l'analyse et retourner le résultat
        log_agent(self.name, input_data, result)
        
        # Log verbeux si activé
        if self.verbosity:
            self._log_verbose_analysis(result, campaign_id or niche)
        
        return result
    
    def _analyze_campaign(self, prompt_template, campaign_data, output_format, result):
        """
        Analyse complète d'une campagne
        """
        # Construire le prompt pour l'analyse
        prompt = prompt_template.replace("{{operation}}", "analyze_campaign")
        prompt = prompt.replace("{{campaign_data}}", json.dumps(campaign_data, ensure_ascii=False))
        prompt = prompt.replace("{{output_format}}", output_format)
        
        # Appeler GPT-4.1 pour l'analyse
        analysis = ask_gpt_4_1(prompt)
        
        # Récupérer les résultats
        result["analysis"] = analysis
        result["metrics"] = analysis.get("metrics", {})
        result["insights"] = analysis.get("insights", [])
        result["status"] = "COMPLETED"
        
        # Générer des visualisations si format graphique demandé
        if output_format == "chart" or output_format == "dashboard":
            result["visualizations"] = self._generate_visualizations(analysis, campaign_data)
        
        # Sauvegarder l'analyse
        report_path = self._save_analysis(analysis, campaign_data.get("campaign_id", "unknown"), "campaign_analysis")
        result["report_path"] = report_path
        
        return result
    
    def _identify_performance_levers(self, prompt_template, campaign_data, output_format, result):
        """
        Identifie les leviers de performance pour une campagne/niche
        """
        # Construire le prompt pour l'identification des leviers
        prompt = prompt_template.replace("{{operation}}", "identify_levers")
        prompt = prompt.replace("{{campaign_data}}", json.dumps(campaign_data, ensure_ascii=False))
        prompt = prompt.replace("{{output_format}}", output_format)
        
        # Appeler GPT-4.1 pour l'analyse
        levers_analysis = ask_gpt_4_1(prompt)
        
        # Récupérer les résultats
        result["levers"] = levers_analysis.get("performance_levers", [])
        result["channel_analysis"] = levers_analysis.get("channel_analysis", {})
        result["message_analysis"] = levers_analysis.get("message_analysis", {})
        result["target_analysis"] = levers_analysis.get("target_analysis", {})
        result["recommendations"] = levers_analysis.get("recommendations", [])
        result["status"] = "COMPLETED"
        
        # Générer des visualisations si format graphique demandé
        if output_format == "chart" or output_format == "dashboard":
            result["visualizations"] = self._generate_lever_visualizations(levers_analysis)
        
        # Sauvegarder l'analyse
        report_path = self._save_analysis(levers_analysis, campaign_data.get("campaign_id", "unknown"), "levers_analysis")
        result["report_path"] = report_path
        
        return result
    
    def _compare_campaigns(self, prompt_template, campaign_data, comparison_data, output_format, result):
        """
        Compare deux campagnes pour identifier les différences et les points forts
        """
        # Construire le prompt pour la comparaison
        prompt = prompt_template.replace("{{operation}}", "compare_campaigns")
        prompt = prompt.replace("{{campaign_data}}", json.dumps(campaign_data, ensure_ascii=False))
        prompt = prompt.replace("{{comparison_data}}", json.dumps(comparison_data, ensure_ascii=False))
        prompt = prompt.replace("{{output_format}}", output_format)
        
        # Appeler GPT-4.1 pour l'analyse
        comparison = ask_gpt_4_1(prompt)
        
        # Récupérer les résultats
        result["comparison"] = comparison
        result["differences"] = comparison.get("differences", {})
        result["strengths"] = comparison.get("strengths", {})
        result["recommendations"] = comparison.get("recommendations", [])
        result["status"] = "COMPLETED"
        
        # Générer des visualisations si format graphique demandé
        if output_format == "chart" or output_format == "dashboard":
            result["visualizations"] = self._generate_comparison_visualizations(comparison, campaign_data, comparison_data)
        
        # Sauvegarder l'analyse
        report_path = self._save_analysis(comparison, 
                                          f"{campaign_data.get('campaign_id', 'unknown')}_vs_{comparison_data.get('campaign_id', 'unknown')}", 
                                          "comparison_analysis")
        result["report_path"] = report_path
        
        return result
    
    def _predict_performance(self, prompt_template, campaign_data, output_format, result):
        """
        Prédit les performances futures d'une campagne en cours
        """
        # Construire le prompt pour la prédiction
        prompt = prompt_template.replace("{{operation}}", "predict_performance")
        prompt = prompt.replace("{{campaign_data}}", json.dumps(campaign_data, ensure_ascii=False))
        prompt = prompt.replace("{{output_format}}", output_format)
        
        # Appeler GPT-4.1 pour l'analyse
        prediction = ask_gpt_4_1(prompt)
        
        # Récupérer les résultats
        result["prediction"] = prediction
        result["projected_metrics"] = prediction.get("projected_metrics", {})
        result["confidence_score"] = prediction.get("confidence_score", 0)
        result["factors"] = prediction.get("influential_factors", [])
        result["status"] = "COMPLETED"
        
        # Générer des visualisations si format graphique demandé
        if output_format == "chart" or output_format == "dashboard":
            result["visualizations"] = self._generate_prediction_visualizations(prediction, campaign_data)
        
        # Sauvegarder l'analyse
        report_path = self._save_analysis(prediction, campaign_data.get("campaign_id", "unknown"), "performance_prediction")
        result["report_path"] = report_path
        
        return result
    
    def _generate_visualizations(self, analysis, campaign_data):
        """
        Génère des visualisations basées sur l'analyse
        """
        visualizations = []
        
        # Créer des visualisations à partir des données d'analyse
        # Ici nous générons des structures JSON qui peuvent être transformées en graphiques
        
        # 1. Graphique des conversions
        if "metrics" in analysis and "conversion_rate" in analysis["metrics"]:
            conversion_chart = {
                "chart_type": "bar",
                "title": "Taux de conversion par étape",
                "data": {
                    "labels": ["Visite", "Lead", "Qualification", "Conversion"],
                    "datasets": [{
                        "label": "Taux (%)",
                        "data": [
                            100,
                            analysis["metrics"].get("lead_rate", 0) * 100,
                            analysis["metrics"].get("qualification_rate", 0) * 100,
                            analysis["metrics"].get("conversion_rate", 0) * 100
                        ],
                        "backgroundColor": ["#4285F4", "#34A853", "#FBBC05", "#EA4335"]
                    }]
                },
                "options": {
                    "scales": {
                        "y": {
                            "beginAtZero": True,
                            "title": {
                                "display": True,
                                "text": "Pourcentage (%)"
                            }
                        }
                    }
                }
            }
            visualizations.append(conversion_chart)
        
        # 2. Graphique temporel des performances
        if "time_series" in analysis:
            time_series = analysis["time_series"]
            time_chart = {
                "chart_type": "line",
                "title": "Évolution des performances dans le temps",
                "data": {
                    "labels": time_series.get("dates", []),
                    "datasets": [{
                        "label": "Leads",
                        "data": time_series.get("leads", []),
                        "borderColor": "#4285F4",
                        "tension": 0.1
                    }, {
                        "label": "Conversions",
                        "data": time_series.get("conversions", []),
                        "borderColor": "#34A853",
                        "tension": 0.1
                    }]
                },
                "options": {
                    "scales": {
                        "y": {
                            "beginAtZero": True,
                            "title": {
                                "display": True,
                                "text": "Nombre"
                            }
                        }
                    }
                }
            }
            visualizations.append(time_chart)
        
        # 3. Graphique de répartition des sources de trafic
        if "traffic_sources" in analysis:
            traffic_sources = analysis["traffic_sources"]
            traffic_chart = {
                "chart_type": "pie",
                "title": "Répartition des sources de trafic",
                "data": {
                    "labels": list(traffic_sources.keys()),
                    "datasets": [{
                        "data": list(traffic_sources.values()),
                        "backgroundColor": ["#4285F4", "#34A853", "#FBBC05", "#EA4335", "#FF6D01", "#46BDC6"]
                    }]
                },
                "options": {
                    "plugins": {
                        "legend": {
                            "position": "right"
                        }
                    }
                }
            }
            visualizations.append(traffic_chart)
        
        return visualizations
    
    def _generate_lever_visualizations(self, levers_analysis):
        """
        Génère des visualisations spécifiques aux leviers de performance
        """
        visualizations = []
        
        # 1. Graphique des leviers de performance
        if "performance_levers" in levers_analysis:
            levers = levers_analysis["performance_levers"]
            lever_names = [lever.get("name", f"Levier {i+1}") for i, lever in enumerate(levers)]
            lever_impacts = [lever.get("impact_score", 0) * 100 for lever in levers]
            
            levers_chart = {
                "chart_type": "horizontalBar",
                "title": "Impact des leviers de performance",
                "data": {
                    "labels": lever_names,
                    "datasets": [{
                        "label": "Impact (%)",
                        "data": lever_impacts,
                        "backgroundColor": "#4285F4"
                    }]
                },
                "options": {
                    "indexAxis": "y",
                    "scales": {
                        "x": {
                            "beginAtZero": True,
                            "title": {
                                "display": True,
                                "text": "Impact (%)"
                            }
                        }
                    }
                }
            }
            visualizations.append(levers_chart)
        
        # 2. Graphique d'analyse des canaux
        if "channel_analysis" in levers_analysis:
            channels = levers_analysis["channel_analysis"]
            channel_chart = {
                "chart_type": "radar",
                "title": "Performance par canal",
                "data": {
                    "labels": list(channels.keys()),
                    "datasets": [{
                        "label": "Performance",
                        "data": [channel.get("performance_score", 0) * 100 for channel in channels.values()],
                        "backgroundColor": "rgba(66, 133, 244, 0.2)",
                        "borderColor": "#4285F4",
                        "pointBackgroundColor": "#4285F4"
                    }, {
                        "label": "Coût-efficacité",
                        "data": [channel.get("cost_efficiency", 0) * 100 for channel in channels.values()],
                        "backgroundColor": "rgba(52, 168, 83, 0.2)",
                        "borderColor": "#34A853",
                        "pointBackgroundColor": "#34A853"
                    }]
                },
                "options": {
                    "scales": {
                        "r": {
                            "beginAtZero": True,
                            "max": 100
                        }
                    }
                }
            }
            visualizations.append(channel_chart)
        
        # 3. Graphique d'analyse des messages
        if "message_analysis" in levers_analysis:
            messages = levers_analysis["message_analysis"]
            message_types = list(messages.keys())
            response_rates = [msg.get("response_rate", 0) * 100 for msg in messages.values()]
            
            message_chart = {
                "chart_type": "bar",
                "title": "Taux de réponse par type de message",
                "data": {
                    "labels": message_types,
                    "datasets": [{
                        "label": "Taux de réponse (%)",
                        "data": response_rates,
                        "backgroundColor": "#FBBC05"
                    }]
                },
                "options": {
                    "scales": {
                        "y": {
                            "beginAtZero": True,
                            "title": {
                                "display": True,
                                "text": "Taux de réponse (%)"
                            }
                        }
                    }
                }
            }
            visualizations.append(message_chart)
        
        return visualizations
    
    def _generate_comparison_visualizations(self, comparison, campaign_data, comparison_data):
        """
        Génère des visualisations pour comparer deux campagnes
        """
        visualizations = []
        
        # 1. Graphique comparatif des KPIs
        if "differences" in comparison and "metrics" in comparison["differences"]:
            metrics = comparison["differences"]["metrics"]
            kpi_names = list(metrics.keys())
            campaign_values = [metrics[kpi].get("campaign", 0) * 100 for kpi in kpi_names]
            comparison_values = [metrics[kpi].get("comparison", 0) * 100 for kpi in kpi_names]
            
            kpi_chart = {
                "chart_type": "bar",
                "title": "Comparaison des KPIs",
                "data": {
                    "labels": kpi_names,
                    "datasets": [{
                        "label": f"Campagne {campaign_data.get('campaign_id', 'A')}",
                        "data": campaign_values,
                        "backgroundColor": "#4285F4"
                    }, {
                        "label": f"Campagne {comparison_data.get('campaign_id', 'B')}",
                        "data": comparison_values,
                        "backgroundColor": "#34A853"
                    }]
                },
                "options": {
                    "scales": {
                        "y": {
                            "beginAtZero": True,
                            "title": {
                                "display": True,
                                "text": "Valeur (%)"
                            }
                        }
                    }
                }
            }
            visualizations.append(kpi_chart)
        
        # 2. Graphique de performance relative
        if "strengths" in comparison:
            strengths = comparison["strengths"]
            categories = list(strengths.keys())
            advantage_campaign = [strengths[cat].get("advantage_campaign", 0) * 100 for cat in categories]
            advantage_comparison = [strengths[cat].get("advantage_comparison", 0) * 100 for cat in categories]
            
            # Créer une échelle où les avantages sont positifs/négatifs
            relative_advantage = []
            for i in range(len(categories)):
                if advantage_campaign[i] > advantage_comparison[i]:
                    relative_advantage.append(advantage_campaign[i] - advantage_comparison[i])
                else:
                    relative_advantage.append(-(advantage_comparison[i] - advantage_campaign[i]))
            
            advantage_chart = {
                "chart_type": "horizontalBar",
                "title": "Avantages relatifs par catégorie",
                "data": {
                    "labels": categories,
                    "datasets": [{
                        "label": "Avantage relatif",
                        "data": relative_advantage,
                        "backgroundColor": [val >= 0 and "#4285F4" or "#EA4335" for val in relative_advantage]
                    }]
                },
                "options": {
                    "indexAxis": "y",
                    "scales": {
                        "x": {
                            "title": {
                                "display": True,
                                "text": f"← Avantage {comparison_data.get('campaign_id', 'B')} | Avantage {campaign_data.get('campaign_id', 'A')} →"
                            }
                        }
                    }
                }
            }
            visualizations.append(advantage_chart)
        
        return visualizations
    
    def _generate_prediction_visualizations(self, prediction, campaign_data):
        """
        Génère des visualisations pour les prédictions de performance
        """
        visualizations = []
        
        # 1. Graphique de prédiction temporelle
        if "time_projection" in prediction:
            time_data = prediction["time_projection"]
            
            # Séparer l'historique de la projection
            historical_dates = time_data.get("historical_dates", [])
            projection_dates = time_data.get("projection_dates", [])
            
            historical_values = time_data.get("historical_values", [])
            projected_values = time_data.get("projected_values", [])
            
            time_chart = {
                "chart_type": "line",
                "title": "Projection de performance",
                "data": {
                    "labels": historical_dates + projection_dates,
                    "datasets": [{
                        "label": "Historique",
                        "data": historical_values + [None] * len(projection_dates),
                        "borderColor": "#4285F4",
                        "tension": 0.1
                    }, {
                        "label": "Projection",
                        "data": [None] * len(historical_dates) + projected_values,
                        "borderColor": "#34A853",
                        "borderDash": [5, 5],
                        "tension": 0.1
                    }]
                },
                "options": {
                    "scales": {
                        "y": {
                            "beginAtZero": True,
                            "title": {
                                "display": True,
                                "text": "Performance"
                            }
                        }
                    }
                }
            }
            visualizations.append(time_chart)
        
        # 2. Graphique des facteurs d'influence
        if "influential_factors" in prediction:
            factors = prediction["influential_factors"]
            factor_names = [factor.get("name", f"Facteur {i+1}") for i, factor in enumerate(factors)]
            factor_impacts = [factor.get("impact", 0) * 100 for factor in factors]
            
            factor_chart = {
                "chart_type": "horizontalBar",
                "title": "Facteurs d'influence sur la performance future",
                "data": {
                    "labels": factor_names,
                    "datasets": [{
                        "label": "Impact (%)",
                        "data": factor_impacts,
                        "backgroundColor": [impact >= 0 and "#34A853" or "#EA4335" for impact in factor_impacts]
                    }]
                },
                "options": {
                    "indexAxis": "y",
                    "scales": {
                        "x": {
                            "title": {
                                "display": True,
                                "text": "Impact (%)"
                            }
                        }
                    }
                }
            }
            visualizations.append(factor_chart)
        
        # 3. Jauge de confiance
        if "confidence_score" in prediction:
            confidence = prediction["confidence_score"]
            
            confidence_chart = {
                "chart_type": "gauge",
                "title": "Niveau de confiance de la prédiction",
                "data": {
                    "datasets": [{
                        "value": confidence * 100,
                        "backgroundColor": ["#EA4335", "#FBBC05", "#34A853"],
                        "borderWidth": 0,
                        "valueLabel": f"{confidence * 100}%"
                    }]
                },
                "options": {
                    "needle": {
                        "radiusPercentage": 2,
                        "widthPercentage": 3.2,
                        "lengthPercentage": 80,
                        "color": "rgba(0, 0, 0, 1)"
                    },
                    "valueLabel": {
                        "formatter": "function(value) { return value + '%'; }"
                    }
                }
            }
            visualizations.append(confidence_chart)
        
        return visualizations
    
    def _save_analysis(self, analysis, identifier, analysis_type):
        """
        Sauvegarde l'analyse dans un fichier JSON
        """
        try:
            # Créer le nom du fichier
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"{self.reports_dir}/{analysis_type}_{identifier}_{timestamp}.json"
            
            # Enregistrer l'analyse
            with open(filename, "w") as f:
                json.dump(analysis, f, indent=2)
            
            return filename
        except Exception as e:
            print(f"[{self.name}] ⚠️ Erreur lors de la sauvegarde de l'analyse: {str(e)}")
            return None
    
    def _log_verbose_analysis(self, result, identifier):
        """
        Génère un log verbeux détaillant l'analyse
        """
        try:
            # Créer le nom du fichier de log
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            log_filename = f"{self.reports_dir}/{identifier}_{timestamp}_verbose.log"
            
            # Formater l'explication détaillée
            explanation = [
                f"=== ANALYSE DÉTAILLÉE: {identifier} ===",
                f"Horodatage: {datetime.datetime.now().isoformat()}",
                f"Type d'opération: {result.get('operation', 'unknown')}",
                f"Statut: {result.get('status', 'unknown')}",
                "\n"
            ]
            
            # Ajouter les détails selon le type d'opération
            if result.get("operation") == "analyze_campaign":
                explanation.extend(self._format_campaign_explanation(result))
            elif result.get("operation") == "identify_levers":
                explanation.extend(self._format_levers_explanation(result))
            elif result.get("operation") == "compare_campaigns":
                explanation.extend(self._format_comparison_explanation(result))
            elif result.get("operation") == "predict_performance":
                explanation.extend(self._format_prediction_explanation(result))
            
            # Enregistrer l'explication
            with open(log_filename, "w") as f:
                f.write("\n".join(explanation))
            
            print(f"[{self.name}] 📝 Log verbeux généré: {log_filename}")
            
            return log_filename
        except Exception as e:
            print(f"[{self.name}] ⚠️ Erreur lors de la génération du log verbeux: {str(e)}")
            return None
    
    def _format_campaign_explanation(self, result):
        """
        Formate l'explication détaillée d'une analyse de campagne
        """
        analysis = result.get("analysis", {})
        metrics = analysis.get("metrics", {})
        insights = analysis.get("insights", [])
        
        explanation = [
            "## MÉTRIQUES CLÉS",
            f"- Taux de conversion: {metrics.get('conversion_rate', 0) * 100:.2f}%",
            f"- Coût par lead: {metrics.get('cost_per_lead', 0):.2f}€",
            f"- ROI: {metrics.get('roi', 0) * 100:.2f}%",
            "\n",
            "## INSIGHTS PRINCIPAUX"
        ]
        
        for i, insight in enumerate(insights):
            explanation.append(f"{i+1}. {insight.get('description', '')}")
            explanation.append(f"   Impact: {insight.get('impact', 'Non défini')}")
            explanation.append(f"   Confiance: {insight.get('confidence', 0) * 100:.0f}%")
            explanation.append("")
        
        explanation.extend([
            "\n",
            "## INTERPRÉTATION",
            analysis.get("interpretation", "Aucune interprétation disponible."),
            "\n",
            "## RECOMMANDATIONS"
        ])
        
        for i, recommendation in enumerate(analysis.get("recommendations", [])):
            explanation.append(f"{i+1}. {recommendation}")
        
        return explanation
    
    def _format_levers_explanation(self, result):
        """
        Formate l'explication détaillée d'une analyse de leviers de performance
        """
        levers_analysis = result.get("levers", [])
        channel_analysis = result.get("channel_analysis", {})
        message_analysis = result.get("message_analysis", {})
        recommendations = result.get("recommendations", [])
        
        explanation = [
            "## LEVIERS DE PERFORMANCE IDENTIFIÉS"
        ]
        
        for i, lever in enumerate(levers_analysis):
            explanation.append(f"{i+1}. {lever.get('name', '')}")
            explanation.append(f"   Impact: {lever.get('impact_score', 0) * 100:.1f}%")
            explanation.append(f"   Description: {lever.get('description', 'Non défini')}")
            explanation.append("")
        
        explanation.append("\n## ANALYSE DES CANAUX")
        
        for channel, data in channel_analysis.items():
            explanation.append(f"- {channel}:")
            explanation.append(f"  Performance: {data.get('performance_score', 0) * 100:.1f}%")
            explanation.append(f"  Coût-efficacité: {data.get('cost_efficiency', 0) * 100:.1f}%")
            explanation.append(f"  Observations: {data.get('observations', 'Aucune')}")
            explanation.append("")
        
        explanation.append("\n## ANALYSE DES MESSAGES")
        
        for message_type, data in message_analysis.items():
            explanation.append(f"- Type: {message_type}")
            explanation.append(f"  Taux de réponse: {data.get('response_rate', 0) * 100:.1f}%")
            explanation.append(f"  Efficacité: {data.get('effectiveness', 0) * 100:.1f}%")
            explanation.append(f"  Points forts: {data.get('strengths', 'Non défini')}")
            explanation.append("")
        
        explanation.append("\n## RECOMMANDATIONS D'OPTIMISATION")
        
        for i, recommendation in enumerate(recommendations):
            explanation.append(f"{i+1}. {recommendation}")
        
        return explanation
    
    def _format_comparison_explanation(self, result):
        """
        Formate l'explication détaillée d'une comparaison de campagnes
        """
        comparison = result.get("comparison", {})
        differences = comparison.get("differences", {})
        strengths = comparison.get("strengths", {})
        recommendations = comparison.get("recommendations", [])
        
        campaign_a = result.get("campaign_id", "Campagne A")
        campaign_b = "Campagne B"  # Normalement extrait du contexte
        
        explanation = [
            f"## COMPARAISON: {campaign_a} vs {campaign_b}",
            "\n## DIFFÉRENCES PRINCIPALES"
        ]
        
        # Différences de métriques
        if "metrics" in differences:
            explanation.append("### Métriques")
            for metric, values in differences.get("metrics", {}).items():
                campaign_value = values.get("campaign", 0) * 100
                comparison_value = values.get("comparison", 0) * 100
                diff = campaign_value - comparison_value
                explanation.append(f"- {metric}: {campaign_value:.1f}% vs {comparison_value:.1f}% (Diff: {diff:+.1f}%)")
            explanation.append("")
        
        # Différences de cibles
        if "audience" in differences:
            explanation.append("### Audience")
            for audience_aspect, values in differences.get("audience", {}).items():
                explanation.append(f"- {audience_aspect}:")
                explanation.append(f"  {campaign_a}: {values.get('campaign', 'Non défini')}")
                explanation.append(f"  {campaign_b}: {values.get('comparison', 'Non défini')}")
            explanation.append("")
        
        explanation.append("\n## FORCES RELATIVES")
        
        for category, data in strengths.items():
            explanation.append(f"### {category}")
            advantage_a = data.get("advantage_campaign", 0) * 100
            advantage_b = data.get("advantage_comparison", 0) * 100
            
            if advantage_a > advantage_b:
                explanation.append(f"Avantage pour {campaign_a}: +{advantage_a - advantage_b:.1f}%")
                explanation.append(f"Raison: {data.get('reason_campaign', 'Non spécifié')}")
            elif advantage_b > advantage_a:
                explanation.append(f"Avantage pour {campaign_b}: +{advantage_b - advantage_a:.1f}%")
                explanation.append(f"Raison: {data.get('reason_comparison', 'Non spécifié')}")
            else:
                explanation.append("Performances équivalentes")
            
            explanation.append("")
        
        explanation.append("\n## ENSEIGNEMENTS")
        
        for insight in comparison.get("insights", []):
            explanation.append(f"- {insight}")
        
        explanation.append("\n## RECOMMANDATIONS")
        
        for i, recommendation in enumerate(recommendations):
            explanation.append(f"{i+1}. {recommendation}")
        
        return explanation
    
    def _format_prediction_explanation(self, result):
        """
        Formate l'explication détaillée d'une prédiction de performance
        """
        prediction = result.get("prediction", {})
        projected_metrics = result.get("projected_metrics", {})
        factors = result.get("factors", [])
        confidence = result.get("confidence_score", 0)
        
        explanation = [
            "## PRÉDICTION DE PERFORMANCE",
            f"Niveau de confiance: {confidence * 100:.1f}%",
            "\n## MÉTRIQUES PROJETÉES"
        ]
        
        for metric, value in projected_metrics.items():
            current = value.get("current", 0) * 100 if isinstance(value.get("current"), float) else value.get("current", 0)
            projected = value.get("projected", 0) * 100 if isinstance(value.get("projected"), float) else value.get("projected", 0)
            change = value.get("change", 0) * 100 if isinstance(value.get("change"), float) else value.get("change", 0)
            
            explanation.append(f"- {metric}:")
            explanation.append(f"  Actuel: {current:.1f}%" if isinstance(current, float) else f"  Actuel: {current}")
            explanation.append(f"  Projeté: {projected:.1f}%" if isinstance(projected, float) else f"  Projeté: {projected}")
            explanation.append(f"  Évolution: {change:+.1f}%" if isinstance(change, float) else f"  Évolution: {change}")
            explanation.append("")
        
        explanation.append("\n## FACTEURS D'INFLUENCE")
        
        for i, factor in enumerate(factors):
            impact = factor.get("impact", 0) * 100
            sign = "+" if impact >= 0 else ""
            explanation.append(f"{i+1}. {factor.get('name', '')} ({sign}{impact:.1f}%)")
            explanation.append(f"   Description: {factor.get('description', 'Non défini')}")
            explanation.append(f"   Confiance: {factor.get('confidence', 0) * 100:.0f}%")
            explanation.append("")
        
        explanation.append("\n## ANALYSE DE TENDANCE")
        
        for trend in prediction.get("trends", []):
            explanation.append(f"- {trend}")
        
        explanation.append("\n## ACTIONS RECOMMANDÉES")
        
        for i, action in enumerate(prediction.get("recommended_actions", [])):
            explanation.append(f"{i+1}. {action}")
        
        return explanation
