"""add is_important to contact_messages

Revision ID: 003_contact_important
Revises: 002_cms_tables
Create Date: 2026-07-22
"""
from alembic import op
import sqlalchemy as sa


revision = "003_contact_important"
down_revision = "002_cms_tables"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "contact_messages",
        sa.Column("is_important", sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade():
    op.drop_column("contact_messages", "is_important")
