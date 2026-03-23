"""merge existing head with gap coverage branch

Revision ID: m1_merge_gap
Revises: afd998d01c9f, k6f7g8h9i0j1
Create Date: 2026-06-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'm1_merge_gap'
down_revision: Union[str, None] = ('afd998d01c9f', 'k6f7g8h9i0j1')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
