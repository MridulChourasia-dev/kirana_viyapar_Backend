"""Add missing timestamp columns to invoice_item.

Revision ID: 009_add_invoice_item_timestamps
Revises: 008_add_invoice_item_table
Create Date: 2026-03-14 15:59:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '009_add_invoice_item_timestamps'
down_revision = '008_add_invoice_item_table'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if 'invoice_item' not in inspector.get_table_names():
        return

    columns = {c['name'] for c in inspector.get_columns('invoice_item')}

    if 'created_at' not in columns:
        op.add_column(
            'invoice_item',
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=True),
        )

    if 'updated_at' not in columns:
        op.add_column(
            'invoice_item',
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=True),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if 'invoice_item' not in inspector.get_table_names():
        return

    columns = {c['name'] for c in inspector.get_columns('invoice_item')}

    if 'updated_at' in columns:
        op.drop_column('invoice_item', 'updated_at')

    if 'created_at' in columns:
        op.drop_column('invoice_item', 'created_at')
