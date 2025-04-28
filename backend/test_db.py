import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()
database_url = os.getenv("DATABASE_URL")
print(f"Tentative de connexion à: {database_url}")

try:
    engine = create_engine(database_url)
    connection = engine.connect()
    print("Connexion réussie!")
    connection.close()
except Exception as e:
    print(f"Erreur de connexion: {e}") 