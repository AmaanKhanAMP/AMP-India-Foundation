"""soft delete fields for CMS content tables

Revision ID: 005_soft_delete
Revises: 004_password_reset
Create Date: 2026-07-23
"""
from alembic import op
import sqlalchemy as sa


revision = "005_soft_delete"
down_revision = "004_password_reset"
branch_labels = None
depends_on = None

TABLES = [
    "hero_banners",
    "home_projects",
    "home_events",
    "testimonials",
    "featured_events",
    "upcoming_events",
    "gallery_items",
]


def upgrade():
    for table in TABLES:
        op.add_column(
            table,
            sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.false()),
        )
        op.add_column(
            table,
            sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        )
        op.add_column(
            table,
            sa.Column("deleted_by", sa.Integer(), nullable=True),
        )
        op.create_index(f"ix_{table}_is_deleted", table, ["is_deleted"])
        op.create_index(f"ix_{table}_deleted_at", table, ["deleted_at"])
        op.create_foreign_key(
            f"fk_{table}_deleted_by_admin_users",
            table,
            "admin_users",
            ["deleted_by"],
            ["id"],
        )


def downgrade():
    for table in TABLES:
        op.drop_constraint(f"fk_{table}_deleted_by_admin_users", table, type_="foreignkey")
        op.drop_index(f"ix_{table}_deleted_at", table_name=table)
        op.drop_index(f"ix_{table}_is_deleted", table_name=table)
        op.drop_column(table, "deleted_by")
        op.drop_column(table, "deleted_at")
        op.drop_column(table, "is_deleted")
