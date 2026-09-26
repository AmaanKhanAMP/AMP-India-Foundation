"""Create home_gallery_items for homepage Photo Gallery CMS.

Revision ID: 012_home_gallery
Revises: 011_home_projects_trim_fields
Create Date: 2026-08-01
"""

from alembic import op
import sqlalchemy as sa


revision = "012_home_gallery"
down_revision = "011_home_projects_trim_fields"
branch_labels = None
depends_on = None

SEED = [
    (
        1,
        "https://images.unsplash.com/photo-1692269725836-fbd72e98883f?auto=format&fit=crop&w=900&q=80",
        "Indian schoolchildren seated together in a classroom learning session",
    ),
    (
        2,
        "https://images.unsplash.com/photo-1692269725911-87697c558be1?auto=format&fit=crop&w=900&q=80",
        "Two young Indian girls studying at a school desk with notebooks",
    ),
    (
        3,
        "https://images.unsplash.com/photo-1692269725827-699e04a11cdf?auto=format&fit=crop&w=900&q=80",
        "Indian boys reading and studying together during an education support session",
    ),
    (
        4,
        "https://images.unsplash.com/photo-1522661067900-ab829854a57f?auto=format&fit=crop&w=900&q=80",
        "Indian teacher volunteering at a chalkboard to guide students in class",
    ),
    (
        5,
        "https://images.unsplash.com/photo-1759738098462-90ffac98c554?auto=format&fit=crop&w=900&q=80",
        "Rural Indian women engaged in a livelihood weaving and skill development program",
    ),
    (
        6,
        "https://images.unsplash.com/photo-1542810634-71277d95dcbb?auto=format&fit=crop&w=900&q=80",
        "Indian children learning outdoors during a community education outreach program",
    ),
]


def upgrade():
    op.create_table(
        "home_gallery_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("image_url", sa.String(length=500), nullable=False),
        sa.Column("alt_text", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_by", sa.Integer(), sa.ForeignKey("admin_users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_home_gallery_items_status", "home_gallery_items", ["status"])
    op.create_index(
        "ix_home_gallery_items_display_order", "home_gallery_items", ["display_order"]
    )
    op.create_index("ix_home_gallery_items_is_deleted", "home_gallery_items", ["is_deleted"])

    for order, url, alt in SEED:
        safe_alt = alt.replace("'", "''")
        op.execute(
            f"""
            INSERT INTO home_gallery_items
              (image_url, alt_text, status, display_order, is_deleted, created_at, updated_at)
            VALUES
              ('{url}', '{safe_alt}', 'published', {order}, 0, UTC_TIMESTAMP(), UTC_TIMESTAMP())
            """
        )


def downgrade():
    op.drop_table("home_gallery_items")
