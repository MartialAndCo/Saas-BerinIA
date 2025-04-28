from app.database.session import engine
from app.database.base_class import Base

# Créer les tables
Base.metadata.create_all(bind=engine)
