"""add_wo_downtime_and_failure_fields

Revision ID: f1a2b3c4d5e6
Revises: 471b4e4986e2
Create Date: 2025-01-15 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f1a2b3c4d5e6'
down_revision: str = '471b4e4986e2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Downtime tracking fields (WO-6)
    op.add_column('work_order', sa.Column('downtime_start', sa.DateTime(), nullable=True))
    op.add_column('work_order', sa.Column('downtime_end', sa.DateTime(), nullable=True))
    op.add_column('work_order', sa.Column('downtime_hours', sa.Float(), nullable=True))
    # Failure analysis fields (WO-7)
    op.add_column('work_order', sa.Column('cause_code', sa.String(255), nullable=True))
    op.add_column('work_order', sa.Column('remedy_code', sa.String(255), nullable=True))
    op.add_column('work_order', sa.Column('failure_notes', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('work_order', 'failure_notes')
    op.drop_column('work_order', 'remedy_code')
    op.drop_column('work_order', 'cause_code')
    op.drop_column('work_order', 'downtime_hours')
    op.drop_column('work_order', 'downtime_end')
    op.drop_column('work_order', 'downtime_start')
