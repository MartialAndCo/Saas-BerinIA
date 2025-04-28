from sqlalchemy import create_engine, text
from app.core.config import settings

def migrate_db():
    """Mettre à jour la structure de la base de données."""
    # Connexion à la base de données
    engine = create_engine(settings.DATABASE_URL)
    conn = engine.connect()
    
    try:
        print("Début de la migration de la base de données...")
        
        # Vérifier si la colonne full_name existe déjà
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'full_name'
        """))
        
        if result.fetchone() is None:
            print("Ajout de la colonne full_name à la table users...")
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN full_name VARCHAR(255)
            """))
            print("Colonne full_name ajoutée avec succès.")
        else:
            print("La colonne full_name existe déjà.")
        
        # Vérifier si la colonne created_at existe déjà
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'created_at'
        """))
        
        if result.fetchone() is None:
            print("Ajout de la colonne created_at à la table users...")
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            """))
            print("Colonne created_at ajoutée avec succès.")
        else:
            print("La colonne created_at existe déjà.")
        
        # Vérifier si la colonne updated_at existe déjà
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'updated_at'
        """))
        
        if result.fetchone() is None:
            print("Ajout de la colonne updated_at à la table users...")
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE
            """))
            print("Colonne updated_at ajoutée avec succès.")
        else:
            print("La colonne updated_at existe déjà.")
        
        # Mettre à jour les contraintes de non-nullité si nécessaire
        conn.execute(text("""
            ALTER TABLE users 
            ALTER COLUMN email SET NOT NULL
        """))
        
        conn.execute(text("""
            ALTER TABLE users 
            ALTER COLUMN hashed_password SET NOT NULL
        """))
        
        print("Migration terminée avec succès!")
        
    except Exception as e:
        print(f"Erreur lors de la migration: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_db() 