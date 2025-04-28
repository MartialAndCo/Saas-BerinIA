from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from app.database.base_class import Base
from app.core.config import settings

# Import all models to ensure they're registered with the metadata
from app.models.user import User
from app.models.niche import Niche
from app.models.lead import Lead
from app.models.campaign import Campaign
from app.models.agent import Agent

def init_db():
    """Initialize the database by creating all tables."""
    print(f"Using database URL: {settings.DATABASE_URL}")
    
    # Print all tables that should be created
    print("Tables that should be created:")
    for table in Base.metadata.tables.keys():
        print(f"  - {table}")
    
    engine = create_engine(settings.DATABASE_URL)
    
    # Check if tables exist before creating
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    print(f"Existing tables before creation: {existing_tables}")
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Check if tables exist after creating
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    print(f"Existing tables after creation: {existing_tables}")
    
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db() 