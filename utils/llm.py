"""
Utilitaires pour l'interaction avec les modèles de langage (LLM).
"""
import json
import datetime
import os
import logging
from utils.config import get_config

logger = logging.getLogger("llm")
config = get_config()

def ask_gpt_4_1(prompt, temperature=0.7, max_tokens=1024):
    """
    Envoie une requête à GPT-4.1 et retourne la réponse.
    Version simulée pour les tests.
    
    Args:
        prompt: Le prompt à envoyer
        temperature: Paramètre de température (0.0-1.0)
        max_tokens: Nombre maximum de tokens de réponse
        
    Returns:
        str: Réponse formatée en JSON (chaîne de caractères)
    """
    logger.info(f"Simulation de requête GPT-4.1 avec température {temperature}")
    
    # Pour les tests, on simule une réponse
    # Dans une implémentation réelle, nous appellerions l'API OpenAI ou équivalent
    
    # Déterminer le type d'analyse demandée
    analysis_type = "analyze_campaign"  # par défaut
    
    if "exporter intelligemment vers le CRM" in prompt or "CRMExporterAgent" in prompt:
        analysis_type = "crm_export"  # Exportation de leads vers le CRM
    elif "Tu es le cerveau de BerinIA" in prompt:
        analysis_type = "brain_decision"  # Décision stratégique du DecisionBrainAgent
    elif "Tu es un agent stratégique chez BerinIA" in prompt:
        analysis_type = "strategy_niche"  # StrategyAgent cherchant une niche
    elif "identify_levers" in prompt:
        analysis_type = "identify_levers"
    elif "compare_campaigns" in prompt:
        analysis_type = "compare_campaigns"
    elif "predict_performance" in prompt:
        analysis_type = "predict_performance"
    
    # Générer une réponse simulée selon le type d'analyse
    response_dict = None
    
    if analysis_type == "crm_export":
        response_dict = {
            "export_decision": {
                "leads_to_export_now": [
                    {
                        "id": "test_lead_1",
                        "qualite": "WARM",
                        "raison_export": "Lead prioritaire avec fort potentiel"
                    },
                    {
                        "id": "test_lead_3",
                        "qualite": "HOT",
                        "raison_export": "Lead très chaud avec besoin immédiat"
                    }
                ],
                "leads_to_delay": [
                    {
                        "id": "test_lead_2",
                        "qualite": "COLD",
                        "raison_delai": "Lead froid nécessitant plus de qualification",
                        "moment_recommande": "Semaine prochaine"
                    }
                ],
                "batching_strategy": {
                    "methode": "PAR_QUALITE",
                    "explication": "Les leads sont regroupés par niveau de qualité pour permettre une approche personnalisée"
                },
                "system_load_management": {
                    "charge_actuelle": "modérée",
                    "limite_quotidienne_respectee": True,
                    "recommandation_charge": "Continuer les exports au rythme actuel"
                }
            },
            "summary": {
                "total_leads_received": 3,
                "leads_exported_now": 2,
                "leads_delayed": 1,
                "quality_distribution": {
                    "chauds_exportes": 1,
                    "chauds_retardes": 0,
                    "tiedes_exportes": 1,
                    "tiedes_retardes": 0,
                    "froids_exportes": 0,
                    "froids_retardes": 1
                }
            },
            "crm_impact_forecast": {
                "charge_estimee": "L'export actuel représente 10% de la capacité quotidienne",
                "timing_optimal": "L'export en milieu de journée permet un traitement dans l'après-midi",
                "recommandations_futures": "Continuer d'exporter les leads chauds immédiatement"
            }
        }
    elif analysis_type == "strategy_niche":
        # Réponse pour le StrategyAgent (sélection de niche)
        response_dict = {
            "niche": "Avocats spécialisés en droit des affaires",
            "justification": "Les cabinets d'avocats spécialisés en droit des affaires ont souvent des clients à forte valeur qui nécessitent une réactivité immédiate. Leur absence du bureau (audiences, rendez-vous) et leurs horaires chargés entraînent une perte de prospects potentiels. Un standard téléphonique IA et un chatbot permettraient de capturer ces opportunités manquées et de réaliser un premier filtrage.",
            "potentiel_conversion": "élevé",
            "suggestions_message": [
                "Combien de clients potentiels estimez-vous perdre chaque mois à cause d'appels manqués ou sans réponse?",
                "Votre expertise en droit des affaires est précieuse. Pendant vos audiences, qui répond à vos nouveaux clients potentiels?",
                "Notre solution de standard téléphonique IA a permis à des cabinets similaires d'augmenter leur acquisition de clients de 30%"
            ]
        }
    elif analysis_type == "brain_decision":
        # Réponse pour le DecisionBrainAgent
        no_data_available = prompt.count("[]") >= 2  # Vérifie si les listes de campagnes sont vides
        
        if no_data_available:
            # Pas de données disponibles, lancement de nouvelle campagne
            response_dict = {
                "decision_process": [
                    "Analyse des campagnes passées : aucune donnée disponible.",
                    "Analyse des campagnes actives : aucune donnée disponible.",
                    "Analyse des niches inexploitées : aucune donnée disponible.",
                    "Considération du contexte d'initialisation : système en phase de démarrage initial.",
                    "Décision basée sur l'absence de données historiques et la nécessité d'initier l'apprentissage du système."
                ],
                "action": "nouvelle",
                "campagne_cible": None,
                "commentaire": "Aucune campagne existante détectée. Le système doit initialiser une première campagne pour commencer à collecter des données et établir des références de performance. Cette phase initiale est cruciale pour l'apprentissage du système.",
                "priorité": "haute",
                "agents_à_impliquer": [
                    "StrategyAgent",
                    "PlanningAgent",
                    "CampaignStarterAgent", 
                    "ScraperAgent", 
                    "CleanerAgent", 
                    "ClassifierAgent"
                ]
            }
        else:
            # Données disponibles, continuer une campagne existante
            # Dans un cas réel, ce serait basé sur les données existantes
            response_dict = {
                "decision_process": [
                    "Analyse des performances des campagnes passées.",
                    "Évaluation des campagnes actives et leur potentiel.",
                    "Examen des facteurs de conversion et du ROI.",
                    "Analyse des niches de marché et leur saturation.",
                    "Considération des ressources système disponibles."
                ],
                "action": "continuer",
                "campagne_cible": "CAM-001",
                "commentaire": "La campagne Avocats (CAM-001) montre le meilleur taux de conversion et mérite d'être continuée. Ses résultats sont significativement au-dessus de la moyenne et le marché n'est pas saturé.",
                "priorité": "haute",
                "agents_à_impliquer": [
                    "AnalyticsAgent", 
                    "PlanningAgent", 
                    "CampaignStarterAgent", 
                    "ScraperAgent"
                ]
            }
            
    elif analysis_type == "analyze_campaign":
        response_dict = {
            "metrics": {
                "conversion_rate": 0.15,
                "cost_per_lead": 26.5,
                "roi": 1.75,
                "lead_rate": 0.42,
                "qualification_rate": 0.28
            },
            "traffic_sources": {
                "Email": 35,
                "Social": 40,
                "Search": 25
            },
            "time_series": {
                "dates": ["2025-01-15", "2025-02-15", "2025-03-15", "2025-04-15"],
                "leads": [30, 45, 38, 42],
                "conversions": [5, 8, 6, 7]
            },
            "insights": [
                {
                    "description": "La campagne montre une forte croissance des leads sur les canaux sociaux.",
                    "impact": "Positif",
                    "confidence": 0.85
                },
                {
                    "description": "Le coût par lead est 15% plus élevé que la moyenne du secteur.",
                    "impact": "Négatif",
                    "confidence": 0.92
                },
                {
                    "description": "Le message de démonstration a le taux de réponse le plus élevé.",
                    "impact": "Positif",
                    "confidence": 0.78
                }
            ],
            "interpretation": "La campagne performe relativement bien avec un ROI positif, mais il y a des possibilités d'optimisation des coûts. Les canaux sociaux sont particulièrement efficaces.",
            "recommendations": [
                "Augmenter le budget alloué aux canaux sociaux de 20%",
                "Revoir la stratégie email pour améliorer le taux de conversion",
                "Utiliser davantage le message 'demo_offer' qui montre les meilleurs résultats"
            ]
        }
    
    elif analysis_type == "identify_levers":
        response_dict = {
            "performance_levers": [
                {
                    "name": "Ciblage social",
                    "impact_score": 0.45,
                    "description": "Le ciblage des publicités sociales a un impact majeur sur les performances"
                },
                {
                    "name": "Message de démonstration",
                    "impact_score": 0.32,
                    "description": "L'offre de démonstration influence fortement le taux de conversion"
                },
                {
                    "name": "Fréquence d'email",
                    "impact_score": 0.18,
                    "description": "La cadence des emails impacte l'engagement"
                }
            ],
            "channel_analysis": {
                "email": {
                    "performance_score": 0.65,
                    "cost_efficiency": 0.58,
                    "observations": "Performance moyenne mais coût par lead élevé"
                },
                "social": {
                    "performance_score": 0.82,
                    "cost_efficiency": 0.75,
                    "observations": "Meilleure performance globale et bon rapport coût/efficacité"
                },
                "search": {
                    "performance_score": 0.70,
                    "cost_efficiency": 0.62,
                    "observations": "Bonne performance mais relativement coûteux"
                }
            },
            "message_analysis": {
                "value_proposition": {
                    "response_rate": 0.16,
                    "effectiveness": 0.58,
                    "strengths": "Bonne présentation de la valeur mais pourrait être optimisée"
                },
                "case_study": {
                    "response_rate": 0.18,
                    "effectiveness": 0.65,
                    "strengths": "Preuve sociale forte, crédibilité élevée"
                },
                "demo_offer": {
                    "response_rate": 0.20,
                    "effectiveness": 0.72,
                    "strengths": "Appel à l'action clair et proposition de valeur tangible"
                }
            },
            "recommendations": [
                "Concentrer 60% du budget sur les canaux sociaux",
                "Renforcer le message de démonstration sur tous les canaux",
                "Réduire la fréquence des emails mais augmenter leur personnalisation",
                "Segmenter davantage l'audience sur les canaux de recherche"
            ]
        }
    
    elif analysis_type == "compare_campaigns":
        response_dict = {
            "differences": {
                "metrics": {
                    "conversion_rate": {"campaign": 0.15, "comparison": 0.12},
                    "cost_per_lead": {"campaign": 26.5, "comparison": 30.0},
                    "roi": {"campaign": 1.75, "comparison": 1.52}
                },
                "audience": {
                    "sectors": {
                        "campaign": ["Technologie", "Finance", "Services"],
                        "comparison": ["Technologie", "Santé", "Éducation"]
                    },
                    "company_size": {
                        "campaign": "PME",
                        "comparison": "Entreprises"
                    }
                }
            },
            "strengths": {
                "conversion": {
                    "advantage_campaign": 0.6,
                    "advantage_comparison": 0.3,
                    "reason_campaign": "Messages plus ciblés et offre de démonstration efficace"
                },
                "coût": {
                    "advantage_campaign": 0.7,
                    "advantage_comparison": 0.2,
                    "reason_campaign": "Meilleure optimisation des enchères et ciblage plus précis"
                },
                "engagement": {
                    "advantage_campaign": 0.4,
                    "advantage_comparison": 0.5,
                    "reason_comparison": "Contenu plus interactif et créatifs plus attrayants"
                }
            },
            "insights": [
                "La campagne A est plus performante en termes de conversion et de coût par lead",
                "La campagne B génère un meilleur engagement initial, mais convertit moins bien",
                "Les secteurs ciblés ont un impact significatif sur les performances"
            ],
            "recommendations": [
                "Adopter le ciblage précis de la campagne A pour d'autres campagnes",
                "Intégrer les éléments d'engagement de la campagne B dans la campagne A",
                "Tester le message de démonstration de la campagne A sur le secteur Santé"
            ]
        }
    
    elif analysis_type == "predict_performance":
        response_dict = {
            "projected_metrics": {
                "conversion_rate": {
                    "current": 0.15,
                    "projected": 0.18,
                    "change": 0.03
                },
                "cost_per_lead": {
                    "current": 26.5,
                    "projected": 24.0,
                    "change": -2.5
                },
                "roi": {
                    "current": 1.75,
                    "projected": 2.0,
                    "change": 0.25
                },
                "leads_per_month": {
                    "current": 150,
                    "projected": 185,
                    "change": 35
                }
            },
            "confidence_score": 0.82,
            "influential_factors": [
                {
                    "name": "Optimisation du ciblage social",
                    "impact": 0.45,
                    "description": "L'amélioration du ciblage devrait augmenter la qualité des leads",
                    "confidence": 0.9
                },
                {
                    "name": "Saisonnalité du secteur",
                    "impact": 0.25,
                    "description": "La période à venir est historiquement favorable",
                    "confidence": 0.75
                },
                {
                    "name": "Concurrence accrue",
                    "impact": -0.15,
                    "description": "Nouveaux concurrents entrant sur le marché",
                    "confidence": 0.65
                }
            ],
            "time_projection": {
                "historical_dates": ["2025-01-15", "2025-02-15", "2025-03-15", "2025-04-15"],
                "historical_values": [30, 45, 38, 42],
                "projection_dates": ["2025-05-15", "2025-06-15", "2025-07-15"],
                "projected_values": [48, 55, 60]
            },
            "trends": [
                "Tendance à la hausse des conversions sur les réseaux sociaux",
                "Amélioration continue du coût par lead",
                "Stabilisation du taux d'engagement email"
            ],
            "recommended_actions": [
                "Augmenter progressivement le budget social de 15% par mois",
                "Tester deux nouvelles variantes du message de démonstration",
                "Mettre en place un programme de fidélisation pour les leads convertis"
            ]
        }
    else:
        response_dict = {"error": "Type d'analyse non reconnu"}
    
    # Convertir le dictionnaire Python en chaîne JSON
    if response_dict is not None:
        return json.dumps(response_dict, ensure_ascii=False)
    else:
        return json.dumps({"error": "Réponse non générée"}, ensure_ascii=False)
