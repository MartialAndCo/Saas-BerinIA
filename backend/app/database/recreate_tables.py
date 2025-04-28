from sqlalchemy import create_engine
from app.core.config import settings
from app.database.base_class import Base
from app.models.user import User
from app.models.niche import Niche
# Importez tous vos autres modèles ici

def recreate_tables():
    """Recréer toutes les tables dans la base de données."""
    engine = create_engine(settings.DATABASE_URL)
    
    # Supprimer toutes les tables existantes
    Base.metadata.drop_all(bind=engine)
    
    # Créer toutes les tables selon les modèles
    Base.metadata.create_all(bind=engine)
    
    print("Tables recréées avec succès!")

if __name__ == "__main__":
    recreate_tables() 