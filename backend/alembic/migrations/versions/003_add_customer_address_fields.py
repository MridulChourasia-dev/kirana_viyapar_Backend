"""Add billing and shipping address fields to customer table.

Revision ID: 003_add_customer_address_fields
Revises: 002_add_audit_notifications
Create Date: 2026-03-14 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = '003_add_customer_address_fields'
down_revision = '002_add_audit_notifications'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add missing customer table columns."""
    # Add billing_address column
    op.add_column('customer', sa.Column('billing_address', sa.Text(), nullable=True))
    
    # Add shipping_address column
    op.add_column('customer', sa.Column('shipping_address', sa.Text(), nullable=True))
    
    # Add balance column
    op.add_column('customer', sa.Column('balance', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0.00'))


def downgrade() -> None:
    """Remove added customer table columns."""
    # Remove balance column
    op.drop_column('customer', 'balance')
    
    # Remove shipping_address column
    op.drop_column('customer', 'shipping_address')
    
    # Remove billing_address column
    op.drop_column('customer', 'billing_address')
