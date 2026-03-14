"""Update invoice table schema to match SQLAlchemy model.

Revision ID: 007_update_invoice_schema
Revises: 006_make_category_id_nullable
Create Date: 2026-03-14 15:40:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers
revision = '007_update_invoice_schema'
down_revision = '006_make_category_id_nullable'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Update invoice table to match SQLAlchemy model."""
    
    # Add customer snapshot columns
    op.add_column('invoice', sa.Column('customer_name', sa.String(255), nullable=True))
    op.add_column('invoice', sa.Column('customer_phone', sa.String(20), nullable=True))
    op.add_column('invoice', sa.Column('customer_gstin', sa.String(15), nullable=True))
    op.add_column('invoice', sa.Column('billing_address', sa.Text, nullable=True))
    
    # Add detailed tax columns
    op.add_column('invoice', sa.Column('total_cgst', sa.Numeric(14, 2), nullable=True, server_default='0.00'))
    op.add_column('invoice', sa.Column('total_sgst', sa.Numeric(14, 2), nullable=True, server_default='0.00'))
    op.add_column('invoice', sa.Column('total_igst', sa.Numeric(14, 2), nullable=True, server_default='0.00'))
    op.add_column('invoice', sa.Column('total_tax', sa.Numeric(14, 2), nullable=True, server_default='0.00'))
    
    # Add discount column
    op.add_column('invoice', sa.Column('discount_amount', sa.Numeric(14, 2), nullable=True, server_default='0.00'))
    
    # Rename total_amount to grand_total
    op.alter_column('invoice', 'total_amount', new_column_name='grand_total')
    
    # Add IGST flag
    op.add_column('invoice', sa.Column('is_igst', sa.Boolean, nullable=True, server_default='false'))
    
    # Add payment_mode column
    op.add_column('invoice', sa.Column('payment_mode', sa.String(50), nullable=True, server_default='cash'))
    
    # Remove tax_amount column (replaced by detailed tax columns)
    try:
        op.drop_column('invoice', 'tax_amount')
    except Exception:
        pass  # Column might not exist
    
    # Make customer_name NOT NULL (after adding it with a default)
    op.execute("UPDATE invoice SET customer_name = 'Unknown' WHERE customer_name IS NULL")
    op.alter_column('invoice', 'customer_name', nullable=False)


def downgrade() -> None:
    """Revert invoice schema changes."""
    
    # Rename grand_total back to total_amount
    op.alter_column('invoice', 'grand_total', new_column_name='total_amount')
    
    # Add back tax_amount column
    op.add_column('invoice', sa.Column('tax_amount', sa.Numeric(14, 2), server_default='0.00'))
    
    # Remove new columns
    op.drop_column('invoice', 'payment_mode')
    op.drop_column('invoice', 'is_igst')
    op.drop_column('invoice', 'discount_amount')
    op.drop_column('invoice', 'total_tax')
    op.drop_column('invoice', 'total_igst')
    op.drop_column('invoice', 'total_sgst')
    op.drop_column('invoice', 'total_cgst')
    op.drop_column('invoice', 'billing_address')
    op.drop_column('invoice', 'customer_gstin')
    op.drop_column('invoice', 'customer_phone')
    op.drop_column('invoice', 'customer_name')
