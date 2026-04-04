"""Add unique constraint to site.site_code

Revision ID: o4_site_code_uq
Revises: o3_asset_crit_mfg
"""
from alembic import op

revision = "o4_site_code_uq"
down_revision = "o3_asset_crit_mfg"
branch_labels = None
depends_on = None


def upgrade():
    op.create_unique_constraint("uq_site_site_code", "site", ["site_code"])


def downgrade():
    op.drop_constraint("uq_site_site_code", "site", type_="unique")
