"""Add missing invoice_item table.

Revision ID: 008_add_invoice_item_table
Revises: 007_update_invoice_schema
Create Date: 2026-03-14 15:53:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers
revision = '008_add_invoice_item_table'
down_revision = '007_update_invoice_schema'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create invoice_item table required by invoice creation and reports."""

    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if 'invoice_item' in inspector.get_table_names():
        return

    op.create_table(
        'invoice_item',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('invoice_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('product_name', sa.String(length=255), nullable=False),
        sa.Column('hsn_code', sa.String(length=20), nullable=True),
        sa.Column('unit', sa.String(length=20), nullable=True),
        sa.Column('quantity', sa.Numeric(12, 3), nullable=False),
        sa.Column('unit_price', sa.Numeric(12, 2), nullable=False),
        sa.Column('tax_rate', sa.Numeric(5, 2), nullable=False, server_default='0.00'),
        sa.Column('discount_pct', sa.Numeric(5, 2), nullable=False, server_default='0.00'),
        sa.Column('line_subtotal', sa.Numeric(14, 2), nullable=False, server_default='0.00'),
        sa.Column('line_discount', sa.Numeric(14, 2), nullable=False, server_default='0.00'),
        sa.Column('taxable_amount', sa.Numeric(14, 2), nullable=False, server_default='0.00'),
        sa.Column('line_cgst', sa.Numeric(14, 2), nullable=False, server_default='0.00'),
        sa.Column('line_sgst', sa.Numeric(14, 2), nullable=False, server_default='0.00'),
        sa.Column('line_igst', sa.Numeric(14, 2), nullable=False, server_default='0.00'),
        sa.Column('line_total', sa.Numeric(14, 2), nullable=False, server_default='0.00'),
        sa.ForeignKeyConstraint(['invoice_id'], ['invoice.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['product_id'], ['product.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_index('ix_invoice_item_invoice_id', 'invoice_item', ['invoice_id'])


def downgrade() -> None:
    """Drop invoice_item table."""

    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if 'invoice_item' not in inspector.get_table_names():
        return

    op.drop_index('ix_invoice_item_invoice_id', table_name='invoice_item')
    op.drop_table('invoice_item')
