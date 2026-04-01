"""Add unique constraint to department_code

Revision ID: o1_dept_code_uq
Revises: n2_rbac_scope
Create Date: 2026-04-01 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op

revision: str = 'o1_dept_code_uq'
down_revision: Union[str, None] = 'n2_rbac_scope'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint('uq_department_department_code', 'department', ['department_code'])


def downgrade() -> None:
    op.drop_constraint('uq_department_department_code', 'department', type_='unique')
