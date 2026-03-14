"""Initial migration - Add core tables: vendor, purchase, expense, role, permissions.

Revision ID: 001_add_erp_models
Revises: 
Create Date: 2026-03-14 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001_add_erp_models'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Create new ERP tables."""
    
    # Create vendor table
    op.create_table(
        'vendor',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('business_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('website', sa.String(500), nullable=True),
        sa.Column('billing_address', sa.Text, nullable=True),
        sa.Column('shipping_address', sa.Text, nullable=True),
        sa.Column('city', sa.String(100), nullable=True),
        sa.Column('state', sa.String(100), nullable=True),
        sa.Column('country', sa.String(100), nullable=True),
        sa.Column('pincode', sa.String(20), nullable=True),
        sa.Column('gstin', sa.String(15), nullable=True),
        sa.Column('pan', sa.String(10), nullable=True),
        sa.Column('bank_account', sa.String(30), nullable=True),
        sa.Column('bank_name', sa.String(255), nullable=True),
        sa.Column('ifsc_code', sa.String(20), nullable=True),
        sa.Column('credit_limit', sa.Numeric(14, 2), server_default='0.00'),
        sa.Column('credit_period_days', sa.Integer, server_default='0'),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['business_id'], ['business.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_vendor_business_id', 'business_id'),
        sa.Index('ix_vendor_name', 'name'),
        sa.Index('ix_vendor_phone', 'phone'),
    )

    # Create purchase table
    op.create_table(
        'purchase',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('business_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('vendor_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('po_number', sa.String(30), nullable=False, unique=True),
        sa.Column('vendor_name', sa.String(255), nullable=False),
        sa.Column('vendor_email', sa.String(255), nullable=True),
        sa.Column('vendor_phone', sa.String(20), nullable=True),
        sa.Column('po_date', sa.Date, nullable=False),
        sa.Column('delivery_date', sa.Date, nullable=True),
        sa.Column('expected_delivery_date', sa.Date, nullable=True),
        sa.Column('status', sa.Enum('DRAFT', 'SENT', 'CONFIRMED', 'RECEIVED', 'INVOICED', 'PAID', 'CANCELLED', name='purchasestatus'), server_default='DRAFT'),
        sa.Column('subtotal', sa.Numeric(14, 2), server_default='0.00'),
        sa.Column('tax_amount', sa.Numeric(14, 2), server_default='0.00'),
        sa.Column('shipping_cost', sa.Numeric(14, 2), server_default='0.00'),
        sa.Column('total', sa.Numeric(14, 2), server_default='0.00'),
        sa.Column('amount_paid', sa.Numeric(14, 2), server_default='0.00'),
        sa.Column('amount_due', sa.Numeric(14, 2), server_default='0.00'),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('terms', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['business_id'], ['business.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['vendor_id'], ['vendor.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_purchase_business_id', 'business_id'),
        sa.Index('ix_purchase_vendor_id', 'vendor_id'),
        sa.Index('ix_purchase_po_number', 'po_number'),
    )

    # Create purchase_item table
    op.create_table(
        'purchase_item',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('business_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('purchase_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('description', sa.String(500), nullable=False),
        sa.Column('quantity', sa.Integer, nullable=False),
        sa.Column('unit', sa.String(50), nullable=False),
        sa.Column('unit_cost', sa.Numeric(12, 2), nullable=False),
        sa.Column('tax_rate', sa.Numeric(5, 2), server_default='0.00'),
        sa.Column('tax_amount', sa.Numeric(12, 2), server_default='0.00'),
        sa.Column('line_total', sa.Numeric(14, 2), nullable=False),
        sa.Column('quantity_received', sa.Integer, server_default='0'),
        sa.Column('quantity_invoiced', sa.Integer, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['business_id'], ['business.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['purchase_id'], ['purchase.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['product_id'], ['product.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_purchase_item_business_id', 'business_id'),
        sa.Index('ix_purchase_item_purchase_id', 'purchase_id'),
        sa.Index('ix_purchase_item_product_id', 'product_id'),
    )

    # Create expense_category table
    op.create_table(
        'expense_category',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('business_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['business_id'], ['business.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_expense_category_business_id', 'business_id'),
        sa.Index('ix_expense_category_name', 'name'),
        sa.UniqueConstraint('business_id', 'name', name='uq_business_expense_category_name'),
    )

    # Create expense table
    op.create_table(
        'expense',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('business_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('category_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('vendor_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('description', sa.String(500), nullable=False),
        sa.Column('amount', sa.Numeric(14, 2), nullable=False),
        sa.Column('expense_date', sa.Date, nullable=False),
        sa.Column('payment_method', sa.String(50), nullable=False),
        sa.Column('reference', sa.String(100), nullable=True),
        sa.Column('tax_amount', sa.Numeric(14, 2), server_default='0.00'),
        sa.Column('has_gst', sa.Boolean, server_default='false'),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['business_id'], ['business.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['category_id'], ['expense_category.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['vendor_id'], ['vendor.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_expense_business_id', 'business_id'),
        sa.Index('ix_expense_category_id', 'category_id'),
        sa.Index('ix_expense_vendor_id', 'vendor_id'),
        sa.Index('ix_expense_expense_date', 'expense_date'),
    )

    # Create permission table
    op.create_table(
        'permission',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('resource', sa.String(100), nullable=False),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('name', sa.String(255), nullable=False, unique=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('category', sa.String(100), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_permission_resource', 'resource'),
        sa.Index('ix_permission_category', 'category'),
        sa.UniqueConstraint('resource', 'action', name='uq_permission_resource_action'),
    )

    # Create role table
    op.create_table(
        'role',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('business_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('is_system_role', sa.Boolean, server_default='false'),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['business_id'], ['business.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_role_business_id', 'business_id'),
    )

    # Create role_permission association table
    op.create_table(
        'role_permission',
        sa.Column('role_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('permission_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['permission_id'], ['permission.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['role_id'], ['role.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('role_id', 'permission_id'),
    )

    # Add custom_role_id to users table
    op.add_column('users', sa.Column('custom_role_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_index('ix_users_custom_role_id', 'users', ['custom_role_id'])
    op.create_foreign_key('fk_users_custom_role_id', 'users', 'role', ['custom_role_id'], ['id'], ondelete='SET NULL')


def downgrade():
    """Revert new ERP tables."""
    
    # Drop foreign key and column from users
    op.drop_constraint('fk_users_custom_role_id', 'users', type_='foreignkey')
    op.drop_index('ix_users_custom_role_id', 'users')
    op.drop_column('users', 'custom_role_id')

    # Drop tables (in reverse order of creation due to FKs)
    op.drop_table('role_permission')
    op.drop_table('role')
    op.drop_table('permission')
    op.drop_table('expense')
    op.drop_table('expense_category')
    op.drop_table('purchase_item')
    op.drop_table('purchase')
    op.drop_table('vendor')
