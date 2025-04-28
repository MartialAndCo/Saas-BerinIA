"""add_date_creation_to_agents

Revision ID: cdcff53e3f7b
Revises: 9b45a789d1e2
Create Date: 2025-04-25 16:56:11.825220

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cdcff53e3f7b'
down_revision: Union[str, None] = '9b45a789d1e2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Ajouter uniquement la colonne date_creation à la table agents
    op.add_column('agents', sa.Column('date_creation', sa.DateTime(), nullable=True, server_default=sa.func.now()))
    
    # Mettre à jour les entrées existantes avec la date actuelle
    op.execute("UPDATE agents SET date_creation = CURRENT_TIMESTAMP WHERE date_creation IS NULL")


def downgrade() -> None:
    """Downgrade schema."""
    # Supprimer la colonne date_creation de la table agents
    op.drop_column('agents', 'date_creation')
    # ### end Alembic commands ###
