from dotenv import load_dotenv
import os
from typing import List, Union, Optional, Any
from pydantic import AnyHttpUrl, validator

# Charger les variables d'environnement depuis .env
load_dotenv()

class Settings:
    # Configuration de l'API
    API_V1_STR: str = "/api"
    API_PREFIX: str = "/api"  # Pour compatibilité avec le code existant
    PROJECT_NAME: str = "BerinIA API"
    
    # Configuration OpenAPI
    OPENAPI_URL: Optional[str] = None  # Laissé à None car configuré dynamiquement dans main.py
    
    # Configuration CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://app.berinia.com",
        "https://app.berinia.com",
        "http://23.88.109.13:3000",
        "http://23.88.109.13:3001",
        "http://23.88.109.13",
        "https://23.88.109.13",
    ]
    
    # Configuration de la base de données
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://berinia_user:tonMotDePasse@localhost/berinia")
    
    # Configuration JWT
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "UneCleSecreteIncassable987654321")
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", 60))
    
    # Configuration admin
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "Bhcmi6pm_")
    
    # Configuration Auth0
    AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN", "votre-tenant.auth0.com")
    AUTH0_AUDIENCE = os.getenv("AUTH0_AUDIENCE", "https://api.berinia.com")
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    def __init__(self):
        self._validate_settings()
    
    def _validate_settings(self):
        """Validate that all required environment variables are set."""
        # Vérifier que les paramètres essentiels sont présents
        if not self.DATABASE_URL:
            raise ValueError("DATABASE_URL must be set in environment or .env file")
        
        if not self.JWT_SECRET_KEY:
            raise ValueError("JWT_SECRET_KEY must be set in environment or .env file")
        
        # Vérifier que l'URL de la base de données est valide
        if not self.DATABASE_URL.startswith("postgresql://"):
            raise ValueError("DATABASE_URL must be a valid PostgreSQL connection string")
        
        # Vérifier que la clé JWT est suffisamment longue
        if len(self.JWT_SECRET_KEY) < 32:
            raise ValueError("JWT_SECRET_KEY should be at least 32 characters long for security")
    
    class Config:
        case_sensitive = True

# Instance unique des paramètres, à importer partout dans l'application
settings = Settings()
