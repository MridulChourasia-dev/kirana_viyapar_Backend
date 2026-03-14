"""Make product category_id nullable.

Revision ID: 006_make_category_id_nullable
Revises: 005_drop_product_unit_enum
Create Date: 2026-03-14 15:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = '006_make_category_id_nullable'
down_revision = '005_drop_product_unit_enum'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Make category_id nullable in product table."""
    op.alter_column('product', 'category_id', existing_type=sa.UUID(), nullable=True)


def downgrade() -> None:
    """Revert category_id to NOT NULL."""
    op.alter_column('product', 'category_id', existing_type=sa.UUID(), nullable=False)
