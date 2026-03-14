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
    """All tables are already created in 000_create_core_tables."""
    pass


def downgrade():
    """All tables cleanup is in 000_create_core_tables."""
    pass
    op.drop_table('audit_log')
