"""Fix product table schema to match SQLAlchemy model.

Revision ID: 004_fix_product_schema
Revises: 003_add_customer_address_fields
Create Date: 2026-03-14 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers
revision = '004_fix_product_schema'
down_revision = '003_add_customer_address_fields'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Fix product table schema to match models."""
    
    # Add missing hsn_code column
    op.add_column('product', sa.Column('hsn_code', sa.String(20), nullable=True))
    
    # Add missing stock_quantity column
    op.add_column('product', sa.Column('stock_quantity', sa.Integer(), nullable=False, server_default='0'))
    
    # Add missing low_stock_alert column
    op.add_column('product', sa.Column('low_stock_alert', sa.Integer(), nullable=False, server_default='10'))
    
    # Rename cost_price to purchase_price
    op.alter_column('product', 'cost_price', new_column_name='purchase_price')
    
    # Rename selling_price to sale_price
    op.alter_column('product', 'selling_price', new_column_name='sale_price')
    
    # Drop mrp column if it exists (no longer used in model)
    try:
        op.drop_column('product', 'mrp')
    except Exception:
        pass  # Column might not exist in all environments
    
    # Drop gst_registration column if it exists (replaced by tax_rate)
    try:
        op.drop_column('product', 'gst_registration')
    except Exception:
        pass  # Column might not exist in all environments


def downgrade() -> None:
    """Revert product schema changes."""
    
    # Add back gst_registration column
    op.add_column('product', sa.Column('gst_registration', sa.Boolean(), server_default='false', nullable=True))
    
    # Add back mrp column
    op.add_column('product', sa.Column('mrp', sa.Numeric(precision=12, scale=2), nullable=True))
    
    # Rename sale_price back to selling_price
    op.alter_column('product', 'sale_price', new_column_name='selling_price')
    
    # Rename purchase_price back to cost_price
    op.alter_column('product', 'purchase_price', new_column_name='cost_price')
    
    # Drop low_stock_alert column
    op.drop_column('product', 'low_stock_alert')
    
    # Drop stock_quantity column
    op.drop_column('product', 'stock_quantity')
    
    # Drop hsn_code column
    op.drop_column('product', 'hsn_code')
