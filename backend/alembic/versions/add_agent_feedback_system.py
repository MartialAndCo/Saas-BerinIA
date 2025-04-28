"""add_agent_feedback_system

Revision ID: 9b45a789d1e2
Revises: e12c0a48171c
Create Date: 2025-04-25 14:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '9b45a789d1e2'
down_revision: Union[str, None] = 'e12c0a48171c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Ajouter les nouvelles colonnes à la table agents
    op.add_column('agents', sa.Column('configuration', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.add_column('agents', sa.Column('prompt_template', sa.Text(), nullable=True))
    op.add_column('agents', sa.Column('metrics', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.add_column('agents', sa.Column('dependencies', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.add_column('agents', sa.Column('log_level', sa.String(), nullable=True, server_default='INFO'))
    op.add_column('agents', sa.Column('feedback_score', sa.Float(), nullable=True, server_default='0.0'))
    op.add_column('agents', sa.Column('last_feedback_date', sa.DateTime(), nullable=True))
    
    # Créer la nouvelle table agent_logs
    op.create_table(
        'agent_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('agent_id', sa.Integer(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.Column('operation', sa.String(), nullable=True),
        sa.Column('input_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('output_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('execution_time', sa.Float(), nullable=True),
        sa.Column('feedback_score', sa.Float(), nullable=True),
        sa.Column('feedback_text', sa.Text(), nullable=True),
        sa.Column('feedback_source', sa.String(), nullable=True, server_default='auto'),
        sa.Column('feedback_timestamp', sa.DateTime(), nullable=True),
        sa.Column('feedback_validated', sa.Boolean(), nullable=True, server_default='False'),
        sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_agent_logs_agent_id'), 'agent_logs', ['agent_id'], unique=False)
    op.create_index(op.f('ix_agent_logs_id'), 'agent_logs', ['id'], unique=False)


def downgrade():
    # Supprimer la table agent_logs
    op.drop_index(op.f('ix_agent_logs_id'), table_name='agent_logs')
    op.drop_index(op.f('ix_agent_logs_agent_id'), table_name='agent_logs')
    op.drop_table('agent_logs')
    
    # Supprimer les colonnes ajoutées
    op.drop_column('agents', 'last_feedback_date')
    op.drop_column('agents', 'feedback_score')
    op.drop_column('agents', 'log_level')
    op.drop_column('agents', 'dependencies')
    op.drop_column('agents', 'metrics')
    op.drop_column('agents', 'prompt_template')
    op.drop_column('agents', 'configuration')
