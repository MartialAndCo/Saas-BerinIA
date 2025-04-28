from __future__ import with_statement
import sys
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from sqlalchemy.ext.declarative import declarative_base
from alembic import context

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

# Get database URL from environment variable
database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise ValueError("DATABASE_URL environment variable is not set")

# Add the app directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import all models to ensure they're registered with the metadata
from app.database.base_class import Base
from app.models.user import User
from app.models.niche import Niche
from app.models.lead import Lead
from app.models.campaign import Campaign
from app.models.agent import Agent
from app.models.agent_log import AgentLog

# This line configures Alembic to use the database URL from the environment variable
config = context.config
config.set_main_option('sqlalchemy.url', database_url)

# Set up the metadata
target_metadata = Base.metadata

# Configure logging
fileConfig(config.config_file_name)

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    print("Running migrations offline is not supported")
else:
    run_migrations_online()
