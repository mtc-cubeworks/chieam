"""Add unique constraint to account_code

Revision ID: o2_acct_code_uq
Revises: o1_dept_code_uq
Create Date: 2026-04-01 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op

revision: str = 'o2_acct_code_uq'
down_revision: Union[str, None] = 'o1_dept_code_uq'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint('uq_account_account_code', 'account', ['account_code'])


def downgrade() -> None:
    op.drop_constraint('uq_account_account_code', 'account', type_='unique')
