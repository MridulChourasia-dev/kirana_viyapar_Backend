"""Drop ProductUnit enum type.

Revision ID: 005_drop_product_unit_enum
Revises: 004_fix_product_schema
Create Date: 2026-03-14 16:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers
revision = '005_drop_product_unit_enum'
down_revision = '004_fix_product_schema'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Drop ProductUnit enum type."""
    op.get_bind().execute(text('DROP TYPE IF EXISTS productunit CASCADE'))


def downgrade() -> None:
    """Re-create ProductUnit enum type."""
    pass  # Not implemented for downgrade
