"""add_logs_columns

Revision ID: e12c0a48171c
Revises: 352cb78921d3
Create Date: 2025-04-23 14:48:07.737007

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e12c0a48171c'
down_revision: Union[str, None] = '352cb78921d3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('logs', sa.Column('type', sa.String()))
    op.add_column('logs', sa.Column('action', sa.String()))
    op.add_column('logs', sa.Column('description', sa.Text()))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('logs', 'description')
    op.drop_column('logs', 'action')
    op.drop_column('logs', 'type')
