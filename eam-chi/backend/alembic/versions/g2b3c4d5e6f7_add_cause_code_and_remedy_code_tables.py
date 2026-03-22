"""add_cause_code_and_remedy_code_tables

Revision ID: g2b3c4d5e6f7
Revises: f1a2b3c4d5e6
Create Date: 2025-01-15 10:01:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'g2b3c4d5e6f7'
down_revision: str = 'f1a2b3c4d5e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'cause_code',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('code', sa.String(100), nullable=True),
        sa.Column('cause_name', sa.String(255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category_of_failure', sa.String(50), sa.ForeignKey('category_of_failure.id'), nullable=True),
        sa.Column('site', sa.String(50), sa.ForeignKey('site.id'), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.String(50), nullable=True),
        sa.Column('updated_by', sa.String(50), nullable=True),
    )
    op.create_table(
        'remedy_code',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('code', sa.String(100), nullable=True),
        sa.Column('remedy_name', sa.String(255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category_of_failure', sa.String(50), sa.ForeignKey('category_of_failure.id'), nullable=True),
        sa.Column('site', sa.String(50), sa.ForeignKey('site.id'), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.String(50), nullable=True),
        sa.Column('updated_by', sa.String(50), nullable=True),
    )


def downgrade() -> None:
    op.drop_table('remedy_code')
    op.drop_table('cause_code')
