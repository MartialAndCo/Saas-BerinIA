"""
Module de simulation de données pour tester les agents sans accès aux bases de données
Ce module fournit des données simulées pour permettre le test des agents
sans nécessiter l'accès aux bases de données réelles.
"""

import json
import random
import datetime
from typing import Tuple, List, Dict, Any

# Niches d'exemple pour la simulation
EXAMPLE_NICHES = [
    "avocats droit des affaires",
    "plombiers urgence",
    "cabinets dentaires privés",
    "agences immobilières de luxe",
    "comptables freelance",
    "psychologues en ligne",
    "architectes d'intérieur",
    "services de nettoyage professionnel",
    "consultants marketing digital",
    "développeurs web indépendants",
    "coachs sportifs à domicile",
    "écoles de langues privées",
    "vétérinaires à domicile",
    "traducteurs juridiques",
    "organisateurs d'événements",
]

# Locations d'exemple
EXAMPLE_LOCATIONS = [
    "Paris", "Lyon", "Marseille", "Bordeaux", "Lille", 
    "Toulouse", "Nice", "Nantes", "Strasbourg", "Montpellier"
]

def generate_campaign_id() -> str:
    """Génère un ID de campagne unique"""
    timestamp = int(datetime.datetime.now().timestamp())
    suffix = random.randint(1000, 9999)
    return f"CAM_{timestamp}_{suffix}"

def generate_past_campaign() -> Dict[str, Any]:
    """Génère une campagne passée simulée"""
    start_date = datetime.datetime.now() - datetime.timedelta(days=random.randint(30, 180))
    end_date = start_date + datetime.timedelta(days=random.randint(7, 30))
    
    # Générer des métriques de performance aléatoires
    lead_count = random.randint(20, 200)
    qualified_count = int(lead_count * random.uniform(0.3, 0.8))
    conversion_count = int(qualified_count * random.uniform(0.1, 0.5))
    
    # Calculer les taux
    qualification_rate = qualified_count / lead_count if lead_count > 0 else 0
    conversion_rate = conversion_count / qualified_count if qualified_count > 0 else 0
    global_success = conversion_rate > 0.2  # Succès si taux de conversion > 20%
    
    return {
        "campaign_id": generate_campaign_id(),
        "niche": random.choice(EXAMPLE_NICHES),
        "location": random.choice(EXAMPLE_LOCATIONS),
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "metrics": {
            "lead_count": lead_count,
            "qualified_count": qualified_count,
            "conversion_count": conversion_count,
            "qualification_rate": qualification_rate,
            "conversion_rate": conversion_rate,
            "cost_per_lead": random.uniform(5, 50),
            "cost_per_conversion": random.uniform(50, 500)
        },
        "success": global_success,
        "feedback": random.choice([
            "Excellente niche avec fort potentiel",
            "Niche moyenne, à optimiser",
            "Résultats décevants, à abandonner",
            "Prometteur mais nécessite plus de données",
            "Bons résultats initiaux"
        ])
    }

def generate_active_campaign() -> Dict[str, Any]:
    """Génère une campagne active simulée"""
    start_date = datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 20))
    
    # Générer des métriques de performance aléatoires pour une campagne en cours
    lead_count = random.randint(5, 50)
    qualified_count = int(lead_count * random.uniform(0.3, 0.8))
    conversion_count = int(qualified_count * random.uniform(0.05, 0.3))
    
    # Calculer les taux
    qualification_rate = qualified_count / lead_count if lead_count > 0 else 0
    conversion_rate = conversion_count / qualified_count if qualified_count > 0 else 0
    
    # Pour une campagne active, on génère aussi des tendances
    trend = random.choice(["improving", "stable", "declining"])
    
    return {
        "campaign_id": generate_campaign_id(),
        "niche": random.choice(EXAMPLE_NICHES),
        "location": random.choice(EXAMPLE_LOCATIONS),
        "start_date": start_date.isoformat(),
        "status": "active",
        "metrics": {
            "lead_count": lead_count,
            "qualified_count": qualified_count,
            "conversion_count": conversion_count,
            "qualification_rate": qualification_rate,
            "conversion_rate": conversion_rate,
            "cost_per_lead": random.uniform(5, 50),
            "cost_per_conversion": random.uniform(50, 500)
        },
        "trend": trend,
        "last_update": datetime.datetime.now().isoformat()
    }

def generate_underexplored_niche() -> Dict[str, Any]:
    """Génère une niche inexploitée simulée"""
    potential_score = random.uniform(0.5, 0.95)
    competition_level = random.uniform(0.1, 0.8)
    
    # Liste des mots-clés associés
    keywords = []
    for _ in range(random.randint(3, 8)):
        keywords.append(f"keyword_{random.randint(1000, 9999)}")
    
    return {
        "niche": random.choice([n for n in EXAMPLE_NICHES if random.random() > 0.7]),
        "source": random.choice(["keyword_research", "market_analysis", "competitor_intel", "qdrant_similarity"]),
        "potential_score": potential_score,
        "competition_level": competition_level,
        "opportunity_score": potential_score * (1 - competition_level),
        "keywords": keywords,
        "discovery_date": (datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 30))).isoformat()
    }

def simulate_get_campaign_data() -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Simule la fonction get_campaign_data() de db/postgres.py"""
    # Générer des campagnes passées
    past_campaigns = []
    for _ in range(random.randint(5, 15)):
        past_campaigns.append(generate_past_campaign())
    
    # Générer des campagnes actives
    active_campaigns = []
    for _ in range(random.randint(1, 5)):
        active_campaigns.append(generate_active_campaign())
    
    return past_campaigns, active_campaigns

def simulate_get_underexplored_niches() -> List[Dict[str, Any]]:
    """Simule la fonction get_underexplored_niches() de memory/qdrant.py"""
    # Générer des niches inexploitées
    niches = []
    for _ in range(random.randint(3, 10)):
        niches.append(generate_underexplored_niche())
    
    return niches

# Patching des fonctions réelles pour utiliser les simulations
def patch_functions():
    """
    Remplace les fonctions réelles par des simulations pour les tests
    Cela permet de tester les agents sans nécessiter d'accès aux bases de données
    """
    from db import postgres
    from memory import qdrant
    
    # Sauvegarder les fonctions originales
    original_get_campaign_data = getattr(postgres, 'get_campaign_data', None)
    original_get_underexplored_niches = getattr(qdrant, 'get_underexplored_niches', None)
    
    # Remplacer par les simulations
    postgres.get_campaign_data = simulate_get_campaign_data
    qdrant.get_underexplored_niches = simulate_get_underexplored_niches
    
    print("🔄 Fonctions de base de données remplacées par des simulations")
    
    # Retourner une fonction pour restaurer les originales
    def restore_functions():
        if original_get_campaign_data:
            postgres.get_campaign_data = original_get_campaign_data
        if original_get_underexplored_niches:
            qdrant.get_underexplored_niches = original_get_underexplored_niches
        print("🔄 Fonctions de base de données originales restaurées")
    
    return restore_functions
