"""add_asset_maintenance_history_table

Revision ID: h3c4d5e6f7g8
Revises: g2b3c4d5e6f7
Create Date: 2025-01-15 10:02:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'h3c4d5e6f7g8'
down_revision: str = 'g2b3c4d5e6f7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'asset_maintenance_history',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('asset', sa.String(50), sa.ForeignKey('asset.id'), nullable=True),
        sa.Column('work_order', sa.String(50), sa.ForeignKey('work_order.id'), nullable=True),
        sa.Column('work_order_activity', sa.String(50), sa.ForeignKey('work_order_activity.id'), nullable=True),
        sa.Column('maintenance_type', sa.String(100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('completed_date', sa.DateTime(), nullable=True),
        sa.Column('downtime_hours', sa.Float(), nullable=True),
        sa.Column('total_cost', sa.Float(), nullable=True),
        sa.Column('category_of_failure', sa.String(50), sa.ForeignKey('category_of_failure.id'), nullable=True),
        sa.Column('cause_code', sa.String(255), nullable=True),
        sa.Column('remedy_code', sa.String(255), nullable=True),
        sa.Column('site', sa.String(50), sa.ForeignKey('site.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.String(50), nullable=True),
        sa.Column('updated_by', sa.String(50), nullable=True),
    )


def downgrade() -> None:
    op.drop_table('asset_maintenance_history')
