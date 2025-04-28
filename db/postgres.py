"""
Module d'accès à la base de données PostgreSQL.
Fonctions utilitaires pour les requêtes communes.
"""

import os
from datetime import datetime, timedelta
import random  # Pour simulation
from db.campaign_storage import (
    get_all_campaigns, get_campaign_by_id, save_campaign,
    get_active_campaigns as get_storage_active_campaigns,
    get_completed_campaigns
)

# Configuration (dans un environnement réel, à charger depuis .env)
DB_HOST = os.getenv("PG_HOST", "localhost")
DB_PORT = os.getenv("PG_PORT", "5432")
DB_NAME = os.getenv("PG_DB", "berinia")
DB_USER = os.getenv("PG_USER", "postgres")
DB_PASS = os.getenv("PG_PASS", "postgres")

class PostgresClient:
    """
    Client pour PostgreSQL qui gère la connexion et les opérations courantes.
    NB: Pour l'instant, ce client simule les actions car nous n'avons pas de DB réelle.
    """
    def __init__(self, host=DB_HOST, port=DB_PORT, dbname=DB_NAME, 
                 user=DB_USER, password=DB_PASS):
        self.connection_params = {
            "host": host,
            "port": port,
            "dbname": dbname,
            "user": user,
            "password": password
        }
        print(f"[PostgresClient] Initialisation (simulation)")
        
    def connect(self):
        """Simule une connexion à PostgreSQL"""
        print(f"[PostgresClient] Connexion simulée à {self.connection_params['host']}:{self.connection_params['port']}/{self.connection_params['dbname']}")
        return True
        
    def execute_query(self, query, params=None):
        """
        Simule l'exécution d'une requête SQL
        Dans l'implémentation réelle, utiliserait psycopg2
        """
        print(f"[PostgresClient] Exécution de requête (simulation): {query}")
        
        # Simulation de résultats pour différents types de requêtes
        if "SELECT" in query and "campaigns" in query:
            return self._simulate_campaign_data()
        elif "SELECT" in query and "leads" in query:
            return self._simulate_lead_data()
        else:
            return []
    
    def _simulate_campaign_data(self):
        """Simule des données de campagne pour les tests"""
        campaigns = [
            {
                "id": "CAM-001",
                "niche": "Avocats",
                "region": "Paris",
                "start_date": (datetime.now() - timedelta(days=30)).isoformat(),
                "end_date": (datetime.now() - timedelta(days=5)).isoformat(),
                "status": "COMPLETED",
                "leads_count": 120,
                "conversion_rate": 5.2
            },
            {
                "id": "CAM-002",
                "niche": "Dentistes",
                "region": "Lyon",
                "start_date": (datetime.now() - timedelta(days=45)).isoformat(),
                "end_date": (datetime.now() - timedelta(days=15)).isoformat(),
                "status": "COMPLETED",
                "leads_count": 85,
                "conversion_rate": 3.8
            },
            {
                "id": "CAM-003",
                "niche": "Architectes",
                "region": "Bordeaux",
                "start_date": (datetime.now() - timedelta(days=20)).isoformat(),
                "end_date": (datetime.now() - timedelta(days=2)).isoformat(),
                "status": "COMPLETED",
                "leads_count": 70,
                "conversion_rate": 7.1
            }
        ]
        return campaigns
    
    def _simulate_lead_data(self):
        """Simule des données de leads pour les tests"""
        lead_statuses = ["NEW", "CONTACTED", "QUALIFIED", "CONVERTED", "LOST"]
        leads = []

        for i in range(50):
            lead = {
                "id": f"LEAD-{1000 + i}",
                "name": f"Entreprise {i}",
                "email": f"contact{i}@example.com",
                "phone": f"06{random.randint(10000000, 99999999)}",
                "source": random.choice(["WEB", "LINKEDIN", "REFERRAL"]),
                "status": random.choice(lead_statuses),
                "created_at": (datetime.now() - timedelta(days=random.randint(1, 60))).isoformat()
            }
            leads.append(lead)

        return leads
        
    def insert_leads(self, leads, campaign_id):
        """
        Insère une liste de leads dans la base de données.
        
        Args:
            leads: Liste de dictionnaires contenant les informations des leads
            campaign_id: Identifiant de la campagne associée
            
        Returns:
            dict: Résultats de l'insertion (nombre de leads insérés, etc.)
        """
        if not leads:
            return {"inserted": 0, "errors": [], "status": "NO_DATA"}
            
        print(f"[PostgresClient] Insertion de {len(leads)} leads pour la campagne {campaign_id} (simulation)")
        
        # Simulation de l'insertion en base de données
        # Dans une implémentation réelle, préparerait une requête INSERT
        
        # Simulation de quelques erreurs d'insertion
        errors = []
        if len(leads) > 10:
            for _ in range(min(len(leads) // 10, 3)):  # Simuler environ 10% d'erreurs, maximum 3
                error_index = random.randint(0, len(leads) - 1)
                errors.append(f"Erreur d'insertion pour le lead {leads[error_index].get('id', 'unknown')}")
        
        inserted_count = len(leads) - len(errors)
        
        # Générer un résultat détaillé
        result = {
            "inserted": inserted_count,
            "errors": errors,
            "status": "SUCCESS" if inserted_count > 0 else "FAILED",
            "campaign_id": campaign_id,
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"[PostgresClient] Résultat de l'insertion: {inserted_count} leads insérés, {len(errors)} erreurs")
        return result

# Fonctions utilitaires pour simplicité d'accès

def get_campaign_performance():
    """
    Récupère les performances des campagnes.
    Pour le moment, simule les données.
    """
    campaigns = [
        "Avocats (Paris, Lyon) - Taux de conversion: 5.2%",
        "Dentistes (Lyon, Marseille) - Taux de conversion: 3.8%",
        "Architectes (Bordeaux) - Taux de conversion: 7.1%",
        "Consultants RH - Taux de conversion: 4.5%"
    ]
    return campaigns

def get_campaign_summary():
    """
    Récupère un résumé des campagnes passées.
    Retourne un dictionnaire avec des valeurs vides ou nulles si aucune donnée n'est disponible.
    """
    # Dans une implémentation réelle, on calculerait ces statistiques depuis la base de données
    # Mais ici on retourne un objet vide
    return {
        "total_campaigns": 0,
        "active_campaigns": 0,
        "completed_campaigns": 0,
        "top_performing_niches": [],
        "underperforming_niches": [],
        "average_conversion_rate": 0,
        "lead_count_total": 0,
        "most_recent_campaign": None
    }

def get_active_campaigns():
    """
    Récupère les campagnes actuellement actives.
    Retourne une liste vide si aucune donnée n'est disponible.
    """
    return []

def is_niche_already_scheduled(niche):
    """
    Vérifie si une niche est déjà planifiée.
    Retourne False si aucune niche n'est planifiée ou si la niche fournie est None.
    """
    if niche is None:
        return False
    
    # Dans une implémentation réelle, on consulterait la base de données
    # pour vérifier si la niche est déjà planifiée
    # Mais ici, on retourne simplement False pour indiquer qu'aucune niche n'est planifiée
    return False

def get_campaign_data():
    """
    Récupère les données des campagnes passées et actives.
    Utilise le système de stockage de fichier JSON pour les campagnes.
    
    Returns:
        tuple: (past_campaigns, active_campaigns)
    """
    print("[PostgresClient] Récupération des données de campagnes...")
    
    # Récupérer les campagnes depuis le stockage
    completed = get_completed_campaigns()
    active = get_storage_active_campaigns()
    
    print(f"[PostgresClient] {len(completed)} campagnes passées, {len(active)} campagnes actives")
    
    return completed, active
