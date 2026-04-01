"""Widen asset.criticality to varchar(50) and convert asset.manufacturer to FK

Revision ID: o3_asset_crit_mfg
Revises: o2_acct_code_uq
Create Date: 2025-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = "o3_asset_crit_mfg"
down_revision = "o2_acct_code_uq"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Widen criticality from varchar(10) to varchar(50)
    op.alter_column(
        "asset",
        "criticality",
        type_=sa.String(50),
        existing_type=sa.String(10),
        existing_nullable=True,
    )

    # 2. Clear any manufacturer values that don't match a manufacturer.id
    op.execute("""
        UPDATE asset
        SET manufacturer = NULL
        WHERE manufacturer IS NOT NULL
          AND manufacturer NOT IN (SELECT id FROM manufacturer)
    """)

    # 3. Alter manufacturer column from varchar(255) to varchar(50)
    op.alter_column(
        "asset",
        "manufacturer",
        type_=sa.String(50),
        existing_type=sa.String(255),
        existing_nullable=True,
    )

    # 4. Add foreign key constraint
    op.create_foreign_key(
        "fk_asset_manufacturer",
        "asset",
        "manufacturer",
        ["manufacturer"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint("fk_asset_manufacturer", "asset", type_="foreignkey")
    op.alter_column(
        "asset",
        "manufacturer",
        type_=sa.String(255),
        existing_type=sa.String(50),
        existing_nullable=True,
    )
    op.alter_column(
        "asset",
        "criticality",
        type_=sa.String(10),
        existing_type=sa.String(50),
        existing_nullable=True,
    )
