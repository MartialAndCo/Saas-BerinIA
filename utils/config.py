"""
Module de gestion de la configuration et des paramètres d'environnement.
Centralise l'accès aux variables d'environnement et aux clés API.
"""

import os
import logging
from dotenv import load_dotenv
from pathlib import Path

# Configuration du logging
logger = logging.getLogger(__name__)

class Config:
    """
    Classe de gestion de la configuration de l'infrastructure IA.
    Charge les variables d'environnement et fournit un accès centralisé.
    """
    
    _instance = None
    
    def __new__(cls):
        """Implémentation singleton pour garantir une seule instance"""
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialise la configuration si ce n'est pas déjà fait"""
        if self._initialized:
            return
            
        # Rechercher le fichier .env dans différents emplacements
        env_paths = [
            Path(".env"),
            Path("config/.env"),
            Path("../config/.env"),
            Path(os.path.join(os.path.dirname(__file__), "../config/.env"))
        ]
        
        env_loaded = False
        for env_path in env_paths:
            if env_path.exists():
                logger.info(f"Chargement des variables d'environnement depuis {env_path}")
                load_dotenv(dotenv_path=str(env_path))
                env_loaded = True
                break
        
        if not env_loaded:
            logger.warning("Aucun fichier .env trouvé, utilisation des variables d'environnement système")
        
        # Initialiser les paramètres
        self._load_params()
        self._initialized = True
        
        # Vérifier les paramètres requis
        self._validate_essential_params()
    
    def _load_params(self):
        """Charge les paramètres depuis les variables d'environnement"""
        # API Keys
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.apify_api_key = os.getenv("APIFY_API_KEY")
        self.apollo_api_key = os.getenv("APOLLO_API_KEY")
        
        # DB Config
        self.database_url = os.getenv("DATABASE_URL")
        
        # Vector DB Config
        self.qdrant_host = os.getenv("QDRANT_HOST", "localhost")
        self.qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))
        
        # Agent Config
        self.apify_daily_limit = int(os.getenv("APIFY_DAILY_LIMIT", "1000"))
        self.apollo_daily_limit = int(os.getenv("APOLLO_DAILY_LIMIT", "500"))
        self.openai_embedding_limit = int(os.getenv("OPENAI_EMBEDDING_LIMIT", "1000"))
        
        # Service Config
        self.agents_api_port = int(os.getenv("AGENTS_API_PORT", "8555"))
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        
        # Security
        self.jwt_secret = os.getenv("JWT_SECRET")
        self.jwt_expire_minutes = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))
    
    def _validate_essential_params(self):
        """Vérifie que les paramètres essentiels sont définis"""
        missing_params = []
        
        # Paramètres requis pour le fonctionnement de base
        if not self.openai_api_key:
            logger.warning("OPENAI_API_KEY manquante, les fonctionnalités LLM seront en mode simulation")
            missing_params.append("OPENAI_API_KEY")
        
        if not self.apify_api_key:
            logger.warning("APIFY_API_KEY manquante, le scraping Apify sera en mode simulation")
            missing_params.append("APIFY_API_KEY")
            
        if not self.apollo_api_key:
            logger.warning("APOLLO_API_KEY manquante, le scraping Apollo sera en mode simulation")
            missing_params.append("APOLLO_API_KEY")
        
        # Paramètres de sécurité
        if not self.jwt_secret:
            logger.warning("JWT_SECRET manquante, l'authentification API sera désactivée")
            missing_params.append("JWT_SECRET")
        
        # Informer des paramètres manquants
        if missing_params:
            logger.warning(f"Paramètres manquants: {', '.join(missing_params)}. "
                        f"Copiez config/.env.example vers config/.env et configurez ces paramètres.")
    
    def get_log_level(self):
        """Convertit le niveau de log en constante logging"""
        levels = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        return levels.get(self.log_level.upper(), logging.INFO)
    
    def is_development_mode(self):
        """Détermine si l'application est en mode développement"""
        return os.getenv("ENV", "development").lower() == "development"
    
    def get_openai_api_key(self):
        """Récupère la clé API OpenAI avec vérification"""
        if not self.openai_api_key or self.openai_api_key.startswith("sk-your-"):
            logger.warning("Clé API OpenAI non configurée ou invalide")
            return None
        return self.openai_api_key
    
    def get_apify_api_key(self):
        """Récupère la clé API Apify avec vérification"""
        if not self.apify_api_key or self.apify_api_key.startswith("apify_api_your-"):
            logger.warning("Clé API Apify non configurée ou invalide")
            return None
        return self.apify_api_key
    
    def get_apollo_api_key(self):
        """Récupère la clé API Apollo avec vérification"""
        if not self.apollo_api_key or self.apollo_api_key == "apollo-api-key-here":
            logger.warning("Clé API Apollo non configurée ou invalide")
            return None
        return self.apollo_api_key

# Instance unique de la configuration
config = Config()

# Fonction pour accéder facilement à la configuration
def get_config():
    return config
