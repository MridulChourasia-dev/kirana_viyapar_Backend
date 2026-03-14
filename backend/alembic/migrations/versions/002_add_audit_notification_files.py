"""Add audit logging and notifications tables.

Revision ID: 002_add_audit_notifications
Revises: 001_add_erp_models
Create Date: 2026-03-14 12:01:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '002_add_audit_notifications'
down_revision = '001_add_erp_models'
branch_labels = None
depends_on = None


def upgrade():
    """Create audit, notification, and settings tables."""

    # Create audit_log table
    op.create_table(
        'audit_log',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('business_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('entity_type', sa.String(50), nullable=False),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('description', sa.String(500), nullable=False),
        sa.Column('old_values', sa.Text, nullable=True),
        sa.Column('new_values', sa.Text, nullable=True),
        sa.Column('ip_address', sa.String(50), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['business_id'], ['business.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_audit_log_business_id', 'business_id'),
        sa.Index('ix_audit_log_user_id', 'user_id'),
        sa.Index('ix_audit_log_entity_type', 'entity_type'),
        sa.Index('ix_audit_log_action', 'action'),
        sa.Index('ix_audit_log_timestamp', 'timestamp'),
    )

    # Create notification table
    op.create_table(
        'notification',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('business_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('type', sa.Enum('INVOICE', 'PAYMENT', 'PURCHASE', 'INVENTORY', 'EXPENSE', 'ALERT', 'SYSTEM', 'OTHER', name='notificationtype'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('message', sa.Text, nullable=False),
        sa.Column('entity_type', sa.String(50), nullable=True),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('action_url', sa.String(500), nullable=True),
        sa.Column('is_read', sa.Boolean, server_default='false'),
        sa.Column('send_email', sa.Boolean, server_default='false'),
        sa.Column('send_sms', sa.Boolean, server_default='false'),
        sa.Column('send_push', sa.Boolean, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['business_id'], ['business.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_notification_business_id', 'business_id'),
        sa.Index('ix_notification_user_id', 'user_id'),
        sa.Index('ix_notification_type', 'type'),
        sa.Index('ix_notification_is_read', 'is_read'),
    )

    # Create settings table
    op.create_table(
        'settings',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('business_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('key', sa.String(255), nullable=False),
        sa.Column('value', sa.Text, nullable=False),
        sa.Column('category', sa.String(100), nullable=False),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('data_type', sa.String(50), server_default='string'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['business_id'], ['business.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_settings_business_id', 'business_id'),
        sa.Index('ix_settings_key', 'key'),
        sa.Index('ix_settings_category', 'category'),
    )


def downgrade():
    """Revert audit, notification, and settings tables."""

    op.drop_table('settings')
    op.drop_table('notification')
    op.drop_table('audit_log')
