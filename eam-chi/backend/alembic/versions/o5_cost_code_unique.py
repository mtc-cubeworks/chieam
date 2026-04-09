"""Add unique constraint to cost_code.code

Revision ID: o5_cost_code_uq
Revises: o4_site_code_uq
"""
from alembic import op

revision = "o5_cost_code_uq"
down_revision = "o4_site_code_uq"
branch_labels = None
depends_on = None


def upgrade():
    op.create_unique_constraint("uq_cost_code_code", "cost_code", ["code"])


def downgrade():
    op.drop_constraint("uq_cost_code_code", "cost_code", type_="unique")
