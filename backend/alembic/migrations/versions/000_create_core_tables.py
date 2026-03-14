"""Initial migration - Create all core tables.

Revision ID: 000_create_core_tables
Revises: 
Create Date: 2026-03-14 07:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '000_create_core_tables'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Create all core tables."""
    
    # Create business table
    op.create_table(
        'business',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('address', sa.String(500), nullable=True),
        sa.Column('city', sa.String(100), nullable=True),
        sa.Column('state', sa.String(100), nullable=True),
        sa.Column('country', sa.String(100), nullable=True),
        sa.Column('pincode', sa.String(20), nullable=True),
        sa.Column('gstin', sa.String(15), nullable=True, unique=True),
        sa.Column('pan', sa.String(10), nullable=True, unique=True),
        sa.Column('logo_url', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_business_email', 'email'),
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
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['business_id'], ['business.id'], ondelete='CASCADE'),
        sa.Index('ix_role_business_id', 'business_id'),
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
        sa.UniqueConstraint('resource', 'action', name='uq_permission_resource_action'),
        sa.Index('ix_permission_resource', 'resource'),
        sa.Index('ix_permission_name', 'name'),
        sa.Index('ix_permission_category', 'category'),
    )

    # Create role_permission association table
    op.create_table(
        'role_permission',
        sa.Column('role_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('permission_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.PrimaryKeyConstraint('role_id', 'permission_id'),
        sa.ForeignKeyConstraint(['role_id'], ['role.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['permission_id'], ['permission.id'], ondelete='CASCADE'),
    )

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('phone', sa.String(20), nullable=True, unique=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('role', sa.String(50), nullable=False, server_default='staff'),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('business_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('custom_role_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['business_id'], ['business.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['custom_role_id'], ['role.id'], ondelete='SET NULL'),
        sa.Index('ix_users_email', 'email'),
        sa.Index('ix_users_business_id', 'business_id'),
    )

    # Create category table
    op.create_table(
        'category',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('business_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('business_id', 'name', name='uq_business_category_name'),
        sa.ForeignKeyConstraint(['business_id'], ['business.id'], ondelete='CASCADE'),
        sa.Index('ix_category_business_id', 'business_id'),
    )

    # Create product table
    op.create_table(
        'product',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('business_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('category_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('sku', sa.String(100), nullable=True, unique=True),
        sa.Column('barcode', sa.String(255), nullable=True, unique=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('unit', sa.String(50), nullable=False),
        sa.Column('cost_price', sa.Numeric(12, 2), nullable=False),
        sa.Column('selling_price', sa.Numeric(12, 2), nullable=False),
        sa.Column('mrp', sa.Numeric(12, 2), nullable=True),
        sa.Column('tax_rate', sa.Numeric(5, 2), server_default='0.00'),
        sa.Column('gst_registration', sa.Boolean, server_default='false'),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('image_url', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['business_id'], ['business.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['category_id'], ['category.id'], ondelete='SET NULL'),
        sa.Index('ix_product_business_id', 'business_id'),
        sa.Index('ix_product_category_id', 'category_id'),
    )

    # Create customer table
    op.create_table(
        'customer',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('business_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('gstin', sa.String(15), nullable=True),
        sa.Column('address', sa.String(500), nullable=True),
        sa.Column('city', sa.String(100), nullable=True),
        sa.Column('state', sa.String(100), nullable=True),
        sa.Column('country', sa.String(100), nullable=True),
        sa.Column('pincode', sa.String(20), nullable=True),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('business_id', 'email', name='uq_business_customer_email'),
        sa.ForeignKeyConstraint(['business_id'], ['business.id'], ondelete='CASCADE'),
        sa.Index('ix_customer_business_id', 'business_id'),
    )

    # Create invoice table
    op.create_table(
        'invoice',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('business_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('customer_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('invoice_number', sa.String(100), nullable=False),
        sa.Column('invoice_date', sa.Date, nullable=False),
        sa.Column('due_date', sa.Date, nullable=True),
        sa.Column('status', sa.String(50), server_default='draft'),
        sa.Column('subtotal', sa.Numeric(14, 2), server_default='0.00'),
        sa.Column('tax_amount', sa.Numeric(14, 2), server_default='0.00'),
        sa.Column('total_amount', sa.Numeric(14, 2), server_default='0.00'),
        sa.Column('amount_paid', sa.Numeric(14, 2), server_default='0.00'),
        sa.Column('amount_due', sa.Numeric(14, 2), server_default='0.00'),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('terms', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('business_id', 'invoice_number', name='uq_business_invoice_number'),
        sa.ForeignKeyConstraint(['business_id'], ['business.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['customer_id'], ['customer.id'], ondelete='SET NULL'),
        sa.Index('ix_invoice_business_id', 'business_id'),
        sa.Index('ix_invoice_customer_id', 'customer_id'),
        sa.Index('ix_invoice_status', 'status'),
        sa.Index('ix_invoice_invoice_date', 'invoice_date'),
    )

    # Create payment table
    op.create_table(
        'payment',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('business_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('invoice_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('customer_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('invoice_number', sa.String(100), nullable=False),
        sa.Column('amount', sa.Numeric(14, 2), nullable=False),
        sa.Column('payment_date', sa.Date, nullable=False),
        sa.Column('payment_method', sa.String(50), nullable=False),
        sa.Column('reference_number', sa.String(100), nullable=True),
        sa.Column('invoice_total', sa.Numeric(14, 2), nullable=False),
        sa.Column('balance_before', sa.Numeric(14, 2), nullable=False),
        sa.Column('balance_after', sa.Numeric(14, 2), nullable=False),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['business_id'], ['business.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['invoice_id'], ['invoice.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['customer_id'], ['customer.id'], ondelete='SET NULL'),
        sa.Index('ix_payment_business_id', 'business_id'),
        sa.Index('ix_payment_invoice_id', 'invoice_id'),
        sa.Index('ix_payment_payment_date', 'payment_date'),
    )

    # Create stock_movement table
    op.create_table(
        'stock_movement',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('business_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('movement_type', sa.String(50), nullable=False),
        sa.Column('quantity', sa.Integer, nullable=False),
        sa.Column('reference_type', sa.String(50), nullable=True),
        sa.Column('reference_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['business_id'], ['business.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['product_id'], ['product.id'], ondelete='CASCADE'),
        sa.Index('ix_stock_movement_business_id', 'business_id'),
        sa.Index('ix_stock_movement_product_id', 'product_id'),
        sa.Index('ix_stock_movement_movement_type', 'movement_type'),
    )

    # Create settings table
    op.create_table(
        'settings',
        sa.Column('id', sa.Integer, nullable=False),
        sa.Column('business_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('category', sa.String(100), nullable=False),
        sa.Column('key', sa.String(255), nullable=False),
        sa.Column('value', sa.Text, nullable=False),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('data_type', sa.String(50), server_default='string'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('business_id', 'category', 'key', name='uq_business_setting_key'),
        sa.ForeignKeyConstraint(['business_id'], ['business.id'], ondelete='CASCADE'),
        sa.Index('ix_settings_business_id', 'business_id'),
    )

    # Create file_upload table
    op.create_table(
        'file_upload',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('business_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('original_filename', sa.String(500), nullable=False),
        sa.Column('stored_filename', sa.String(500), nullable=False, unique=True),
        sa.Column('file_type', sa.String(50), nullable=False),
        sa.Column('file_size', sa.Integer, nullable=False),
        sa.Column('extension', sa.String(10), nullable=False),
        sa.Column('storage_path', sa.String(500), nullable=False),
        sa.Column('storage_type', sa.String(50), server_default='local'),
        sa.Column('is_public', sa.Boolean, server_default='false'),
        sa.Column('expiry_days', sa.Integer, nullable=True),
        sa.Column('entity_type', sa.String(50), nullable=True),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['business_id'], ['business.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.Index('ix_file_upload_business_id', 'business_id'),
        sa.Index('ix_file_upload_user_id', 'user_id'),
    )


def downgrade():
    """Drop all core tables."""
    op.drop_table('file_upload')
    op.drop_table('settings')
    op.drop_table('stock_movement')
    op.drop_table('payment')
    op.drop_table('invoice')
    op.drop_table('customer')
    op.drop_table('product')
    op.drop_table('category')
    op.drop_table('users')
    op.drop_table('role_permission')
    op.drop_table('permission')
    op.drop_table('role')
    op.drop_table('business')
