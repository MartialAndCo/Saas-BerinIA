from sqlalchemy import create_engine, text
from app.core.config import settings
from app.models.niche import Niche
from app.core.security import get_password_hash

def seed_db():
    """Seed the database with initial data."""
    # Connexion directe à la base de données
    engine = create_engine(settings.DATABASE_URL)
    conn = engine.connect()
    
    try:
        # Vérifier si des utilisateurs existent déjà
        result = conn.execute(text("SELECT COUNT(*) FROM users"))
        user_count = result.scalar()
        
        if user_count == 0:
            print("Création de l'utilisateur admin...")
            # Insérer directement avec SQL pour éviter les problèmes de modèle
            conn.execute(text("""
                INSERT INTO users (username, email, hashed_password, is_active, is_admin, full_name)
                VALUES (:username, :email, :hashed_password, :is_active, :is_admin, :full_name)
            """), {
                "username": settings.ADMIN_USERNAME,
                "email": settings.ADMIN_USERNAME,
                "hashed_password": get_password_hash(settings.ADMIN_PASSWORD),
                "is_active": True,
                "is_admin": True,
                "full_name": "Admin"
            })
            conn.commit()
            print("Utilisateur admin créé avec succès!")
        else:
            print(f"Des utilisateurs existent déjà ({user_count}), aucun utilisateur créé.")
        
        # Vérifier si des niches existent déjà
        result = conn.execute(text("SELECT COUNT(*) FROM niches"))
        niche_count = result.scalar()
        
        if niche_count == 0:
            print("Création des niches initiales...")
            # Insérer les niches
            niches = [
                {"nom": "Immobilier", "description": "Secteur immobilier résidentiel et commercial"},
                {"nom": "Juridique", "description": "Services juridiques pour particuliers et entreprises"},
                {"nom": "Architecture", "description": "Services d'architecture et de design"},
                {"nom": "Ressources Humaines", "description": "Services RH et recrutement"},
                {"nom": "Santé", "description": "Professionnels de la santé et bien-être"},
                {"nom": "Restauration", "description": "Restaurants et services de restauration"},
                {"nom": "Éducation", "description": "Services éducatifs et formation"},
                {"nom": "Tourisme", "description": "Agences de voyage et services touristiques"}
            ]
            
            for niche in niches:
                conn.execute(text("""
                    INSERT INTO niches (nom, description)
                    VALUES (:nom, :description)
                """), niche)
            
            conn.commit()
            print("Niches créées avec succès!")
        else:
            print(f"Des niches existent déjà ({niche_count}), aucune niche créée.")
            
    except Exception as e:
        print(f"Erreur lors de l'initialisation de la base de données: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    seed_db() 