"""CMS tables: admin users + website content

Revision ID: 002_cms_tables
Revises: 001_contact_messages
Create Date: 2026-07-22

"""
from alembic import op
import sqlalchemy as sa


revision = "002_cms_tables"
down_revision = "001_contact_messages"
branch_labels = None
depends_on = None


def _content_columns(extra):
    cols = [
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        *extra,
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    ]
    return cols


def upgrade():
    op.create_table(
        "admin_users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_admin_users_email", "admin_users", ["email"], unique=True)

    op.create_table(
        "hero_banners",
        *_content_columns(
            [
                sa.Column("image_url", sa.String(length=500), nullable=False),
                sa.Column("title", sa.String(length=255), nullable=False),
                sa.Column("title_accent", sa.String(length=120), nullable=True),
                sa.Column("subtitle", sa.Text(), nullable=True),
                sa.Column("description", sa.Text(), nullable=True),
                sa.Column("primary_btn_text", sa.String(length=100), nullable=True),
                sa.Column("primary_btn_link", sa.String(length=500), nullable=True),
                sa.Column("secondary_btn_text", sa.String(length=100), nullable=True),
                sa.Column("secondary_btn_link", sa.String(length=500), nullable=True),
            ]
        ),
    )
    op.create_index("ix_hero_banners_status", "hero_banners", ["status"])
    op.create_index("ix_hero_banners_display_order", "hero_banners", ["display_order"])

    op.create_table(
        "home_projects",
        *_content_columns(
            [
                sa.Column("image_url", sa.String(length=500), nullable=False),
                sa.Column("title", sa.String(length=255), nullable=False),
                sa.Column("description", sa.Text(), nullable=True),
                sa.Column("button_text", sa.String(length=100), nullable=True),
                sa.Column("button_link", sa.String(length=500), nullable=True),
            ]
        ),
    )
    op.create_index("ix_home_projects_status", "home_projects", ["status"])
    op.create_index("ix_home_projects_display_order", "home_projects", ["display_order"])

    op.create_table(
        "home_events",
        *_content_columns(
            [
                sa.Column("image_url", sa.String(length=500), nullable=False),
                sa.Column("title", sa.String(length=255), nullable=False),
                sa.Column("description", sa.Text(), nullable=True),
                sa.Column("venue", sa.String(length=255), nullable=True),
                sa.Column("event_date", sa.String(length=100), nullable=True),
                sa.Column("event_time", sa.String(length=100), nullable=True),
                sa.Column("registration_link", sa.String(length=500), nullable=True),
                sa.Column("button_text", sa.String(length=100), nullable=True),
                sa.Column("speaker", sa.String(length=255), nullable=True),
            ]
        ),
    )
    op.create_index("ix_home_events_status", "home_events", ["status"])
    op.create_index("ix_home_events_display_order", "home_events", ["display_order"])

    op.create_table(
        "testimonials",
        *_content_columns(
            [
                sa.Column("profile_image", sa.String(length=500), nullable=True),
                sa.Column("name", sa.String(length=120), nullable=False),
                sa.Column("designation", sa.String(length=255), nullable=True),
                sa.Column("organisation", sa.String(length=255), nullable=True),
                sa.Column("location", sa.String(length=255), nullable=True),
                sa.Column("message", sa.Text(), nullable=False),
                sa.Column("rating", sa.Integer(), nullable=False),
            ]
        ),
    )
    op.create_index("ix_testimonials_status", "testimonials", ["status"])
    op.create_index("ix_testimonials_display_order", "testimonials", ["display_order"])

    op.create_table(
        "featured_events",
        *_content_columns(
            [
                sa.Column("banner_image", sa.String(length=500), nullable=False),
                sa.Column("title", sa.String(length=255), nullable=False),
                sa.Column("description", sa.Text(), nullable=True),
                sa.Column("venue", sa.String(length=255), nullable=True),
                sa.Column("event_date", sa.String(length=100), nullable=True),
                sa.Column("event_time", sa.String(length=100), nullable=True),
                sa.Column("category", sa.String(length=100), nullable=True),
                sa.Column("registration_link", sa.String(length=500), nullable=True),
            ]
        ),
    )
    op.create_index("ix_featured_events_status", "featured_events", ["status"])
    op.create_index("ix_featured_events_display_order", "featured_events", ["display_order"])

    op.create_table(
        "upcoming_events",
        *_content_columns(
            [
                sa.Column("image_url", sa.String(length=500), nullable=False),
                sa.Column("title", sa.String(length=255), nullable=False),
                sa.Column("description", sa.Text(), nullable=True),
                sa.Column("venue", sa.String(length=255), nullable=True),
                sa.Column("event_date", sa.String(length=100), nullable=True),
                sa.Column("event_time", sa.String(length=100), nullable=True),
                sa.Column("category", sa.String(length=100), nullable=True),
                sa.Column("registration_link", sa.String(length=500), nullable=True),
            ]
        ),
    )
    op.create_index("ix_upcoming_events_status", "upcoming_events", ["status"])
    op.create_index("ix_upcoming_events_display_order", "upcoming_events", ["display_order"])

    op.create_table(
        "gallery_items",
        *_content_columns(
            [
                sa.Column("image_url", sa.String(length=500), nullable=False),
                sa.Column("title", sa.String(length=255), nullable=False),
                sa.Column("description", sa.Text(), nullable=True),
                sa.Column("category", sa.String(length=100), nullable=True),
                sa.Column("year", sa.String(length=20), nullable=True),
                sa.Column("location", sa.String(length=255), nullable=True),
                sa.Column("alt_text", sa.String(length=255), nullable=True),
            ]
        ),
    )
    op.create_index("ix_gallery_items_status", "gallery_items", ["status"])
    op.create_index("ix_gallery_items_display_order", "gallery_items", ["display_order"])


def downgrade():
    for table in (
        "gallery_items",
        "upcoming_events",
        "featured_events",
        "testimonials",
        "home_events",
        "home_projects",
        "hero_banners",
        "admin_users",
    ):
        op.drop_table(table)
